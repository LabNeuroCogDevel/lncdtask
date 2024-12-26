# LNCD Task

`lncdtask` is a python package providing "computer games" using [psychopy](https://www.psychopy.org/). The exported scripts, classes, and wrappers are tailored to pre-generated (psuedo-random) fixed-timing events for fMRI and EEG tasks with eye tracking. 


## Tasks
| task script | description |
| ------ | ---- |
| `lncd_dollarreward` | reward/neutral antisaccade |
| `lncd_eyecal`       | horz dot visually guided saccade for EOG eye position calibration |
| `lncd_mgs`          | visual guided saccade -> memory guided saccade|
| `lncd_rest`         | eye tracker sync or TR debugging for resting state fMRI |

![](docs/lncd_rest.webm)

## Classes

  * `ExternalCom` - `new`, `start`, `stop`, `event` to external interfaces
    * `Arrington` - interface with Arrington (avotec) eye tracking
    * `Eyelink` - interface with SR Research EyeLink eye tracking Host PC
    * `ParallelPortEEG` - record events to `Status` channel via LPT 8-bit (0-255) "TTL" 
  * `Participant`
  * `RunDialog`
