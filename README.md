# pong
Classic game of Pong with its own computer controlled competitor  
Also has improved, smoother paddle movement  
Made using Pygame

**How the AI works:**  
When the ball is initialized at the center or when the ball collides with a paddle, an invisible "future" ball is spawned and shoots out in the same direction as the visible ball but at a slightly greater speed. The computer paddle will then track this invisible future ball and adjust its position accordingly. This creates the effect of the computer paddle "predicting" where the ball will end up before the ball actually reaches the end.
