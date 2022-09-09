========
lncdtask
========


Psychopy wrapper for tasks run in the LNCD.

Useful where a "task" can be described by the sequence: 

  1. draw function
  2. wait until onset
  3. flip & mark in external sources (e.g. eye tracker event, ttl marker)



Install with pip::

   python3 -m pip install git+https://github.com/LabNeuroCogDevel/lncdtask --user --upgrade
   python3 -m lncdtask.eyecal
   # and/or 
   python3 -m lncdtask.dollarreward


Or clone and inspect `helloworldtask.py`, `lncdtask/eyecal.py`, and  `lncdtask/dollarreward.py` for examples.

For specific sites, see MS Windows read `*.bat` files. 

Features
--------

Provides a generic classes:

* `LNCDTask` with functions

  * `self.flip_at(onset, info1, info2,...)` to wait until onset and send external marks "info1 info2"

  * default colored "+" stims `self.iti` and `self.isi`

  * `run()` over `onset_df` dataframe (columns "`onset`" and "`event_name`", see `add_onsets()`) with functions registered to event_names using `add_event_type()`


* `ExternalCom` and implementations `Arrington` `EyeLink` and `ParallelPortEEG` to send events to external sources.

 * exposes `start()`, `stop()`, `new()`, and `event()`


 * `LNCDTask` takes a list of `ExternalCom` classes and will send events with `AllExternal` in `flip_at()`

   
The task is organized by events rather than trials. The timing dataframe `onset_df` is "long" instead of "wide." This provides a less featured alternative to psychopy.data's TrialHandler2_

Credits
-------

* Free software: GNU General Public License v3

* lncdtask makes heavy use of psychopy_

* This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _TrialHandler2: https://www.psychopy.org/api/data.html#psychopy.data.TrialHandler2
.. _psychopy: https://www.psychopy.org/
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


