### Testing With Tic-Tac-Toe State machine

These tests use tic-tac-toe events with a bitwrap eventstore
using bitwrap schema file named "octoe"

#### How 'octoe' state_machine lets you play tic-tac-toe

    move('BEGIN')

          |  |      turn_x:
        --+--+--    turn_o: 
          |  |
        --+--+--
          |  |

    'BEGIN' sets up the empty board
    --------------------------
    move(<action>)

    subsequent moves use a 3 char encoding

        00|01|02    turn_x: 1
        --+--+--    turn_o: 0
        10|11|12
        --+--+--
        20|21|22

    string: '(X|O)[0-2][0-2]'
    to specify token placment
    --------------------------
    move('X11')

          |  |      turn_x: 1
        --+--+--    turn_o: 0
          |X |
        --+--+--
          |  |

    'X' takes middle center
    --------------------------
    move('O01')

          |O |      turn_x: 0
        --+--+--    turn_o: 1
          |X |
        --+--+--
          |  |

    'O' takes top center

