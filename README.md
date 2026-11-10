# Estimating Pi with Random Points

## What my program does

My program estimates pi by throwing random points into a square. A quarter circle takes up pi/4 of the square, so about pi/4 of the points land inside it. Multiplying the fraction inside by 4 gives an estimate of pi. This is called the Monte Carlo method.

My question: how fast does the error shrink as I use more points?

Probability theory says the typical error should be about 1.642 / sqrt(N), where N is the number of points. That means using 100 times more points should only make the error 10 times smaller. Claude explained this concept to me, and I wanted to test whether it is true.

How it works:

1. For each N from 100 up to 1 billion (100, 1,000, 10,000, ...), the program estimates pi 30 separate times.
2. It measures how spread out those 30 estimates are (the standard deviation) and compares that to the formula.
3. It fits a line on a log-log plot. If the slope is about -0.5, the error shrinks like 1/sqrt(N).

The program runs on one core because it is one loop that handles one batch of points at a time, so extra cores would not be used. The biggest run uses 1 billion points, which would take about 16 GB of memory to make all at once. Making them 1 million at a time only uses about 16 MB and gives the same result (one of my tests checks this), so I only needed to request 512 MB. I used a fixed random seed (2026) so the results are reproducible: anyone who runs the code gets exactly the same numbers, and the tests can check for exact answers.

## How to run it

Set up the environment on Great Lakes:

    git clone https://github.com/elconner87/monte-carlo-pi.git
    cd monte-carlo-pi
    module load mamba
    mamba env create -f environment.yml -p ~/.conda/envs/monte-carlo-pi
    eval "$(conda shell.bash hook)"
    conda activate monte-carlo-pi

Run the tests:

    python -m pytest -v

The tests also run automatically on GitHub Actions every time I push.

Submit the job (change --account in run_job.sh to your own account first):

    mkdir -p logs results
    sbatch run_job.sh
    squeue --me

## My Great Lakes run

- Job ID: 65802063
- Ran on compute node gl3014 (not a login node)
- State: COMPLETED, exit code 0:0
- Time: 6 min 37 s used out of 20 min requested
- Memory: about 132 MB used out of 512 MB requested
- 1 core requested and used

The logs are in logs/, and the job ID, sacct record, and program output are in results/.

## Results

- Slope: -0.508 (theory says -0.5)
- Best estimate: 3.1415853 with 1 billion points (real pi is 3.1415927)
- With 1 billion points, the measured spread was 0.0000502 and the predicted spread was 0.0000519

The full numbers are in results/convergence.csv and the plot is results/convergence.png.

What this means: the results match the theory. The slope of -0.508 is very close to -0.5, and the measured spread is close to the predicted spread at every N. They are not exactly equal because I only did 30 trials per N, so the spread itself is a little uncertain.

The big takeaway is that Monte Carlo is slow to get accurate. Going from 10 million to 1 billion points is 100 times more work, but the error only got 10 times smaller, which is just one more correct decimal place. That is why Monte Carlo simulations need a lot of computing power and are often run on clusters like Great Lakes.

## My tests

The 6 tests in tests/test_monte_carlo_pi.py check that the functions give the right answers:

- test_count_inside: (0,0) is inside, (0.6,0.8) is on the circle (counts as inside), and (0.9,0.9) is outside, so the count is 2.
- test_estimate_pi_is_close: with 1 million points, the estimate is within 0.01 of pi.
- test_same_seed_same_answer: the same seed gives exactly the same answer.
- test_chunks_give_same_answer: splitting the points into batches does not change the answer.
- test_summarize_mean: the average of 3.0, 3.2 and 3.4 is 3.2.
- test_theoretical_std: for N = 1, the formula gives about 1.642.

I worked out the expected values (2, 3.2 and 1.642) by hand.

## AI use and citations

I followed the Lecture 3 guidelines:

- I used Claude to help write the monte-carlo-pi.py program but made sure I understand every line, what it's doing, and why. I asked for explanations when I was unsure so I could check its code even though sometimes I feel limited by my coding ability. Additionally, I asked for an example of a test but wrote all the tests in the file myself and calculated the expected outcomes. 

- I read through every function and the explanations, figured out the test values, made sure the tests pass on GitHub Actions, ran the full job on Great Lakes, and checked that the results match the theory to make sure I understand what was happening and can explain everything.

The code is also marked as AI-assisted in comments at the top of `monte_carlo_pi.py` and the test file. I did not copy code from anywhere else.