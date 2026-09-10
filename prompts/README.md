Prompts are currently embedded in the OpenAI client for a compact first release.

For a larger deployment, move router and answer prompts into versioned files:

router.v1.txt
answer.v1.txt

and load them through a PromptRegistry abstraction.

The important production principle is to version prompts together with evaluation results.
