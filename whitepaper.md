# Solving State Explosion with Petri-Nets and Vector Clocks

#### The Problem

Event driven programming has a problem formally modeling events:
https://en.wikipedia.org/wiki/Event-driven_programming#Criticism

```
Due to the phenomenon known as "state explosion," the complexity of a traditional FSM tends to grow much faster
than the complexity of the reactive system it describes. This happens because the traditional state machine formalism
inflicts repetitions.

https://barrgroup.com/Embedded-Systems/How-To/State-Machines-Event-Driven-Systems
```

### Bitwrap Solution

What is a bitwrap machine?

#### Some Computer Science:

It has primitive elements in common with[Counter Machines](https://en.wikipedia.org/wiki/Counter_machine)

Each machine schema is represented as the "Vector Form" of a [Petri-Net](https://en.wikipedia.org/wiki/Petri_net)

### Vector Form

Given this simple 3-place Petri-Net that models a voting system:

![vote_machine graph](https://bitwrap.github.io/image/vote_machine.png)

* We can represent the state as an array of 'places'.
  * Each place is acted upon by a 'transition' vector.
* We represent an instruction set as a set of deltas
  * Each transition vector maps to a single instruction.
* During an execution
  * Transition vectors are combined with input states using vector addition.
  * Output vectors having only positive scalar integers are valid.

#### State-Vectors

A 3-place Petri-Net - inital state

```
[1,0,0]
```

we execute the 'YAY' instruction
```
 [ 1,0,0]
+[-1,1,0]
 --------
 [ 0,1,0]
```

once this transition happens this graph cannot execute 'YAY' again.


NOTE: Due to the properties of Petri-Nets
the valid range of scalar values is constrained to natural numbers. (integers >=0)

```
 [ 0,1,0]
+[-1,1,0]
 --------
 [-1,2,0] <= invalid state
```

Using this machine as a programing model -
we can easily validate the output of our instruction by testing for any negative scalar values.

#### Playable Tic-Tac-Toe Demo

By using state-vectors designed to model the tic-tac-toe board, we have effectively modeled
a game of tic-tac-to as a deterministic state machine without suffering from 'State Explosion'.

![tic-tac-toe state machine](https://bitwrap.github.io/image/octothorpe.png)

See A 21-place Petri-Net in action: https://bitwrap.github.io/#octothorpe

Read our latests blog post: http://www.blahchain.com
