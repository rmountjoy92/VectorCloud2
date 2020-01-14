Scripts
=======

Script basics
-------------
Scripts in VectorCloud can be as simple as sending one command to Vector to make
him say hello, to hundreds (or thousands) of lines of code, creating complex
routines and behaviors. You've probably seen the bar in VectorCloud that says
"enter a command", when you enter a command in that bar you just ran a script!

Let's make a script! Say we want to make Vector drive off his charger, play an
animation, say something, then drive back on his charger, we would go to the scripts
tab, click add script,  name it "Do things" and give it a description then
enter this in commands:

.. code-block:: python

    robot.behavior.drive_off_charger()
    robot.anim.play_animation('anim_turn_left_01')
    robot.behavior.say_text("Something!")
    robot.behavior.drive_on_charger()

If you've used the sdk before you'll notice that you can use the object robot
without connecting to a Vector, VectorCloud handles that automatically! Click save,
then on the home screen of the web ui, enter:

.. code-block:: python

    script:Do things

In the command bar of the Vector that you want to run the script on.

Script arguments
----------------
Scripts can also have arguments. Arguments are like settings that alter the way
your script runs. Say we have a script named 'Say text' that looks like this:

.. code-block:: python

    robot.behavior.say_text(text)

If you know your python, you can tell that text is not in quotation marks, which means
it's a variable. You should also notice that we did not set the text variable equal to
anything. To set that variable, when we call the script from the command bar,
we'll enter:

.. code-block:: python

    script:Say text?text="hello world"

Result: Vector should say 'hello world'!