# Contract Design Notes

Staring with the concept that a blockchain is an "api for continual agreement".

## What is a contract?
A traditional 'contract' is used to:

1. describe a timeline for future events and expected behavior from agreed parties
2. define incentive or reward for desirable actions or outcomes
3. define fines or penalties for undesirable actions or outcomes

### Contract validation

    "To know the future is to be trapped by it."

Since we cannot effectively model emergent properties of a system of contracts,
we instead focus on providing a useful substrate on which that system can be allowed to grow.

Bitwrap contracts model a constrained set of possible outcomes.
In the event of conflict or error, the contract is "sent to arbitration".

### Contract Evaluation 

Arbitration is provided via a mutually trusted 3rd party algorithm.

The arbiter program evaluates the eventstream over the lifespan of the contract,
and renders a judgement according to it's programming.

As more judgements are decided and published, the algorithm becomes better understood.

### Future

Depending on which arbiter a contract is paired with, it's overall behavior may change dramatically.

Using an arbiter with a contract allows narrowly defined contract programs to be 
composed into more widely applied systems of rules .


