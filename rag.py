from src.retrieval import retrieve
from src.llm import generate_answer
from src.guardrails import validate_output, validate_question


def build_context(results):

    context_parts = []

    for i, result in enumerate(results, start=1):

        context_parts.append(
            f"""
SOURCE {i}
----------------------------------
Source: {result['source']}
PDF Page: {result['page']}
Chunk ID: {result['chunk_id']}
Retrieval Score: {result['score']:.4f}

{result['text']}
"""
        )

    return "\n".join(context_parts)


def answer_question(question):

    # Input guardrail
    valid, error = validate_question(question)

    if not valid:
        return error

    # Retrieve relevant information
    results = retrieve(question)

    # Retrieval guardrail
    if not results:
        return (
            "I could not find sufficient information in the provided "
            "Income-tax Rules 2026 document."
        )

    # Build context with source metadata
    context = build_context(results)

    # Generate grounded answer
    answer = generate_answer(
    question=question,
    context=context
    )
    # Output guardrail
    valid_output, error = validate_output(
    answer,
    results
    )
    if not valid_output:
        return(
        "I could not provide a reliable answer because the "
        "generated response could not be verified against "
        "the retrieved Income-tax Rules 2026 content."
    )
    return answer


if __name__ == "__main__":

    question = input("\nEnter your Income-tax question: ")

    print("\nSearching Income-tax Rules 2026...")

    answer = answer_question(question)

    print("\n" + "=" * 70)
    print("ANSWER")
    print("=" * 70)

    print(answer)