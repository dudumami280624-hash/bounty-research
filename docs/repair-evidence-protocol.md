# Evidence-driven repair acceptance

This project uses the REA principle: evidence, rewrite, compare, verify, and close the loop.

Verified reference: student_lab/contracts/VulnerableVault.sol includes a deliberately vulnerable contract and a corrected teaching implementation. student_lab/test/ReentrancyLesson.t.sol contains the behavioral regression tests.

Training: compare the two local implementations and record the observable difference in state-update ordering and Foundry behavior.

Independent assessment: the model must produce its own candidate without copying the reference implementation. Run Foundry against the generated candidate and retain compiler output, test results, and model output for every attempt.

Passing reference tests is not proof that the model independently repaired a contract. Do not mark autonomous learning or graduation complete without independent, held-out evidence and the required review.
