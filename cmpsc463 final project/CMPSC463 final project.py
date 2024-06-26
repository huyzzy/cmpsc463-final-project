from flask import Flask, render_template, request
import numpy as np

app = Flask(__name__)


def print_matrix(mat):
    output = "<pre>"
    for i in range(len(mat)):
        for j in range(len(mat[i])):
            # Right-align the values with 6 spaces padding for consistency
            output += f"{mat[i][j]:>6.2f} "
        output = output.strip() + "\n"  # Strip trailing spaces and add a newline
    output += "</pre>"
    return output


def match_score(alpha, beta, match_award, gap_penalty, mismatch_penalty):
    if alpha == beta:
        return match_award
    elif alpha == '-' or beta == '-':
        return gap_penalty
    else:
        return mismatch_penalty

def needleman_wunsch(seq1, seq2, gap_penalty, match_award, mismatch_penalty):
    n = len(seq1)
    m = len(seq2)
    score = np.zeros((m + 1, n + 1))
    for i in range(m + 1):
        score[i][0] = gap_penalty * i
    for j in range(n + 1):
        score[0][j] = gap_penalty * j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = score[i - 1][j - 1] + match_score(seq1[j-1], seq2[i-1], match_award, gap_penalty, mismatch_penalty)
            delete = score[i - 1][j] + gap_penalty
            insert = score[i][j - 1] + gap_penalty
            score[i][j] = max(match, delete, insert)
    matrix_output = print_matrix(score)
    align1, align2 = "", ""
    i, j = m, n
    while i > 0 and j > 0:
        score_current = score[i][j]
        if score_current == score[i-1][j-1] + match_score(seq1[j-1], seq2[i-1], match_award, gap_penalty, mismatch_penalty):
            align1 += seq1[j-1]
            align2 += seq2[i-1]
            i -= 1
            j -= 1
        elif score_current == score[i-1][j] + gap_penalty:
            align1 += '-'
            align2 += seq2[i-1]
            i -= 1
        else:
            align1 += seq1[j-1]
            align2 += '-'
            j -= 1
    while j > 0:
        align1 += seq1[j-1]
        align2 += '-'
        j -= 1
    while i > 0:
        align1 += '-'
        align2 += seq2[i-1]
        i -= 1
    align1, align2 = align1[::-1], align2[::-1]
    return align1, align2, matrix_output


@app.route('/', methods=['GET', 'POST'])
def align_sequences():
    result_available = False
    alignment1 = ''
    alignment2 = ''
    matrix = ''
    seq1 = ''
    seq2 = ''
    gap_penalty = -1
    match_award = 1
    mismatch_penalty = -1
    
    if request.method == 'POST':
        seq1 = request.form.get('seq1', '')
        seq2 = request.form.get('seq2', '')
        gap_penalty = int(request.form.get('gap_penalty', -1))
        match_award = int(request.form.get('match_award', 1))
        mismatch_penalty = int(request.form.get('mismatch_penalty', -1))

        # Call the sequence alignment function with all required arguments
        alignment1, alignment2, matrix = needleman_wunsch(seq1, seq2, gap_penalty, match_award, mismatch_penalty)
        result_available = True
    
    # Pass all form data back to the template, whether it was a POST request or not
    return render_template('index.html', result_available=result_available, 
                           alignment1=alignment1, alignment2=alignment2, matrix=matrix,
                           seq1=seq1, seq2=seq2, gap_penalty=gap_penalty,
                           match_award=match_award, mismatch_penalty=mismatch_penalty)

if __name__ == '__main__':
    app.run(debug=True) 
