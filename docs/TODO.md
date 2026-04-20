# UMA MUSUME (UmaPlay) – Backlog (organized)

This organizes the mixed notes into a clear, actionable backlog. Items are grouped by workstream and priority. “Later” holds non-urgent ideas. 

================================================================================

## 0.4



### 0.4.2

Bug:
- Try again race bug, pressing 'RACE' instead
- @Rosetta: it is confusing hanshin juvenively for Asahi hai, if asahi hai is first. Japanese oaks and yushun... Maybe do a full read and go back

ADB:
- Bluestack bugfixes and validation @Pure Fox and others

README.md:
- Updated with instructions for ADB (@Dummiez)
- suggest just open terminal as admin in the worst case
- slice the readme to make easier to read
- Update images
- MuMuPlayer through the localhost:5557 docs
- LDPlayer ADB docs
- INDICATION, DON'T USE POWER SHELL
- people is forgetting activate conda env
- Open Command Prompt and navigate to the Umaplay folder -> installation not clear enough. The Change directory

Discord:
- put icons in discord server... gifs and more
- give points to Dorasu and antonio and others for activity on discord. Gamification give points to who gave me the discord template for git: "I think you may need template for issue report"



- On new races, is confusing the camera button with the skip button. include the new images at datasets\uma_unity_cup\raw\set_2025-11-19 already labeled, to the ura model (normal no unity) with the inspiration class. Retrained

Events:
- adding a new uma trainee, doesn't require only scraping data, we may need to look into internal umamusume assets for the classifier algorithm... document this kind of processes and make the auto validator algorithms. And add the new icons


Bot Strategy (General):
- @Unknown: Okay, new suggestion: If the run is at the URA Finale, it should not rest at least at the final turn before the finals


also look for 'alone' hints / spirits, we may have a support card below. If not recognized a support_card


- @Rosetta:
For Tazuna I have stats > hints for energy overcap priority, but it will still reject dating if energy is high enough even though accepting provides stats and rejecting only a hint (I want energy overcap prevention for her third date)
"""
Author notes: I think this is a bug. This is a problem that should not be happening this way. So we need to investigate what's going on and what this person is trying to to do. This is regarding the energy cap prevention, well, the overflow of energy prevention that we are rotating the options here. But I think it's also related to not only to PALs, but this is also related to in general, because maybe we have this bug also for other support cards, not only for Tasu Nakashimoto or, well, PAL support. Maybe we have this for other ones.
"""


Events:
- how should i respond still fails (chain). Check and validate
- When no event detected, generate a special log in debug folder if 'debug' bool is enabled: gent.py:292: [Event] EventDecision(matched_key=None, matched_key_step=None, pick_option=1, clicked_box=(182.39614868164062, 404.23193359375, 563.8184204101562, 458.83447265625), debug={'current_energy': 64, 'max_energy_cap': 100, 'chain_step_hint': None, 'num_choices': 2, 'has_event_card': False, 'ocr_title': '', 'ocr_description': ''}). 

Bug:
- race.py 867 when getting the style_btns chosen, error of list index out of range


Roseta: Also I don't have a log for it but if it's on fast mode and finds a good training that's capped, it'll return NOOP before checking other trianings and keep looping like that 

Bot Strategy:
One more little idea I've just had - it would be cool if the settings "allow racing over low training" could be expanded into deciding what grades of races this is allowed to trigger with (eg. only G1s)
MagodyBoy — 17:20
and the minimum energy to trigger race, I think right now I check if we have >= 70% of energy

Quality Assurance:
- Color unit testing: detected as yellow the 'green' one "yellow: +0.00"

if ignored hint, don't do deferred check...



mumuplayer test



with f8 also detect the shop

@Unknown

 — 3/11/2025 1:00
Found another "bug" where it stops at Ura races
Stuff I used

thread of 'Unknown'

support_type is confusing pwr and PAL, better use a classiffier or another logic


make it clear:
Thorin

 — 11/11/2025 6:41
Nevermind, I believe I found the solution (Won't delete so people find the solution when searching Discord)

We have to use a Virtual Machine to be able to use our mouse:
https://github.com/Magody/Umaplay/blob/main/docs/README.virtual_machine.md


antonioxxx2

 — 11/11/2025 17:11
estoy viendo que en algunas carreras el mouse queda entremedio de concierto y next

Rosetta — 13/11/2025 13:14
I don't have a log but sometimes when I schedule the Japanese Derby and the recommended race is a random OP one, it'll go for the Japanese Oaks instead - maybe because it's on the first screen and the Derby isn't, but the Satsuki Sho doesn't have this problem


Unknown

 — 15/11/2025 10:14
Weird bug, but the bot buys late surger straightaways when I put pace chaser and pace chaser straightaways on late surger runs
put positive / negative tokens

Rosetta — 15/11/2025 10:16
To fix that go to core\actions\skills.py, edit it in notepad and find the confidence that says 0.75 # experimental and change the 0.75 to 0.9
The only issue I've had since then is firm/wet conditions
But I added that to the skill override json

FreedomArk — 11:00
this is a minor gripe suggestion but is it possible to have a switch where it just stops upon detecting its the crane game? sometimes i leave it in the background on another screen while watching shows and can at least manual the crane game in the off chance it pops up.

override junior only show great and good, doesn't make sense to show the others

daily race kind of fail when shopping

Unity cup:
Put fallback in medium option as default
Buff to single supports friend training -> 1 to 1.1 and make it configurable


cover new events
kashimoto loop when energy overflow, bug





R…

 — Yesterday at 22:34
Name                    CurrentHorizontalResolution CurrentVerticalResolution CurrentRefreshRate
----                    --------------------------- ------------------------- ------------------
Meta Virtual Monitor
NVIDIA GeForce RTX 4070 5120                        1440                      239
its a Samsung Odessey Monitor
Image
Ultra Wide
and for some reason the script forces to work with Procesor chip instead of graphics card can we add an option to launch it with graphics card like nvidia to use CUda properly and the other to use just procesor like intel chip or amd
i changed the script a bit for me to use with my nvidia card and it works way faster 

R…

 — 14/11/2025 19:42
so i just found the two main issues, for some reason i was having conflicts with my CUDA version and it was not detecting it right and second i had HDR enabled in my pc... i just changed the CUDA version to one compativle from Pytorch and disabled HDR.


Claw Machine:
- @Rosetta: Re-check of the logic so it always Win. If first detected plushie is good enough and it is not at the border take it, if not do a full scan. Check the zips on discord.

we have 'silent' yolo detection errors. for example with support_bar, it has 0.31 so it was filtered out before our debug saver
add a check like 'if support type, then you must have support bar, otherwise try again with less confidence


- Weird error check thread, air grove, and infirmary, Rocostre thread: https://discord.com/channels/1100600632659943487/1438783548390641789

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "D:\GitHub\UmAutoplay\main.py", line 333, in _runner
    self.agent_scenario.run(
  File "D:\GitHub\UmAutoplay\core\actions\unity_cup\agent.py", line 486, in run
    if self.waiter.seen(
  File "D:\GitHub\UmAutoplay\core\utils\waiter.py", line 247, in seen
    img, dets = self._snap(tag=tag or (self.cfg.tag + "_seen"))
  File "D:\GitHub\UmAutoplay\core\utils\waiter.py", line 354, in _snap
    img, _, dets = self.yolo_engine.recognize(
  File "D:\GitHub\UmAutoplay\core\perception\yolo\yolo_local.py", line 187, in recognize
    img = self.ctrl.screenshot(region=region)
  File "D:\GitHub\UmAutoplay\core\controllers\adb.py", line 251, in screenshot
    result = self._adb_command("exec-out", "screencap", "-p", text=False)
  File "D:\GitHub\UmAutoplay\core\controllers\adb.py", line 60, in _adb_command
    raise RuntimeError(f"ADB command timed out: {' '.join(cmd)}") from exc
RuntimeError: ADB command timed out: adb -s localhost:5555 exec-out screencap -p


### 0.4.3
optimize CNN predicts with ONNX runtime for CPU automatically

Fat Raccoon

 — 14/11/2025 0:30
Is there any way to increase the speed of the bot or is it meant to stay at that speed to prevent issues?

.315 — 14/11/2025 0:09
The bot always use a clock when failing a race even when i set it to stop on failed race
It uses the clock then stop
I think it mistake the "try again" button for the "next" button
Is there a fix for it ?

wit training of 3+ white spirit is better than other possible good options
improve the seasonal multipliers log

it did rest before the january senior event... even though we will have upgrade in energy and mood
group presets, if one is already active, can't not right click another tab
improve info text in bot strategy policy
if try to change the group a particular item, it is changing the full group

Phalkun

 — 7:07
Idk but most of the time I press F2 again and it didn't stop
So I wonder if pause will be an actual function that show a pop up on the screen like when you press f2 to activate the auto



Phalkun

 — 8:29
just wonder can you add pause (press f2 again or f3 or sth)?
Rosetta — 10:43
Technically you can press F2 again and it will stop
But it then forgets which skills you bought which can sometimes suck (especially if it hangs during a race you don't have a trophy for)


skill positive / negative tokens for pace chacer corners / straightaway and more, like Rosetta



Pure Fox

 — 14:12
it seems like the debut style option is ignored, there is also no option to choose style for later races? so it uses default style for every race afterwards
Image
Pure Fox
 — 14:20
tho in the log it said something about setting style



## 0.5

### 0.5.0
if not skill bought, or if multiple 'disabled' plus icons, that may mean, we don't have more skill points so we can early finish the buy sequence
solve fast mode bugs

Speed up processing:
on android it is very slow
speed up the bot


antonioxxx2

 — Yesterday at 23:42
Is there any way to improve the performance of my Umamusume?
using the bot sometimes, one run = 2hours or 1hour and 30 minutes


Pure Fox
dynamic styling race
 — 17:05
tbh all i really need is late on a few specific races (tss etc)
iris — 17:06
i think another fork has setting style based on race distance, could be an option?



Claw Machine:
ニコラス

 — Yesterday at 22:56
Quick question, does the bot actually work better in full screen? Whenever I did it with the game in windowed mode so I could look at the terminal process, it performs real badly at the claw machine minigame as it often went too far from the plushies.



Add R cards

Bat and executable:
- bat is failing
- Executable in release

Team trial
- Prioritize the ones with 'With every win' (gift)

Skill Buying:
- @EO1: List what skills the bot should prioritize and any that isn't in the selection it will randomally get in the list of skills to automatically pick: like if for the 1st part I know I need a certain uma stamina skill to win, then i would 9/10 times get it first. Add auto buy best option based on running style (with a premade priority list)

Bot Strategy / Policy:
- configurable scoring system for rainbows, explosion, combos
"""@EO1:
I also like to add one other idea, maybe like a prioritize support card you want so like kitasan or maybe Tazuna since I am not sure how pals are intergrated in the script

@Undertaker-86 Issue at Github:
Each card also has a different "rainbow bonus". For instance, the Manhattan Cafe STAM card has 1.2 Friendship multiplier, while Super Creek STAM has 1.375, so Super Creek should nudge the bot to click it more than Manhattan Cafe.
"""
- Put parameter in web ui, to decide when is 'weak' turn based on SV or others configs. """Weak turn classifications is used to decide if go to race, rest or recreation instead of training"""
- Change text to: Allow Racing when 'weak turn'
- @EpharGy: Director / Riko Kashimoto custom configs: option to add more and more weight to the Director with the aim to be green by 2nd Skill  increase check.
- Slight WIT nerf on weak turns (prevent over-weighting).
- put rainbow in hint icon or something like that it is not clear what it is right now
- after two failed retried, change style position to front

Team trials:
- handle 'story unlocked'  (press close button), before shop. And "New High score" message (test on monday)
- infinite loop when nothing to do in team trials but in go button check log 'log_team_trials_0.5.0.txt'
- improve team trials the 6 clicks, check if we are in that screen and do as much or as less clicks as needed instead of precomputing

Shop:
- Error loop in shop when nothing to buy, partial state, check on debug 'log_shop_0.5.0.txt'


- transparent may be happening after pressing 'back' in training
- fix data per trainee, (extra training and others, otherwise fit doesn't work)

Template Matching:
- for 'scenario' how does template matching works? is it used? or only text?

- race scheduler improve the patience when no stars found or similar views. Speed up.
- doc the new data augmentation including data steam checker. We need to keep that in sync with traineed, a way to check if there is consistency or if we have more information or less information in particular areas

@Unknown: do you think you could add a feature to add the minimum fans for the unique upgrade or is that already implemented?


Agent Nav: didn't recognized star pieces and bout shoes, retrain nav with more data

- UX: on hint required skills, only bring the selected on 'skills to buy' to have all in sync, instead of the full list. on required skills make sure standard distance cicle or double circle are the same?

- they added new choices for some events of oguri cap, grass wonders, mejiro mcqueens, mejiro ryan, agnes Tachyon, Sakura Bakushin -> automate the event scrapping

Bug:
- false positive, tried to look for this race on july 1:
10:03:03 INFO    agent.py:789: [planned_race] skip_guard=1 after failure desired='Takarazuka Kinen' key=Y3-06-2
10:03:03 INFO    agent.py:241: [planned_race] scheduled skip reset key=Y3-06-2 cooldown=2
10:03:04 DEBUG   lobby.py:796: [date] prev: DateInfo(raw='Senior Year Early Jun', year_code=3, month=6, half=2). Cand: DateInfo(raw='Senior Year Early Jul', year_code=3, month=7, half=1). accepted: DateInfo(raw='Senior Year Early Jul', year_code=3, month=7, half=1)
10:03:04 INFO    lobby.py:797: [date] monotonic: Y3-Jun-2 -> Y3-Jul-1

- for trainee matcher, train a classifier, for now keep template matching. With label studio train the classifier
- 'pre-process' based on the preset, and use the preprocess to speed up the progress


@Rocostre:
"""
test it in JP version to bring plugins and more:
came across this repository a while back while using the Japanese version, and it worked incredibly well — even to this day. I was wondering if you could take a look at the logic behind it and suggest any possible fixes or improvements on your current project. Not sure if this helps or if you're already familiar with it.

https://github.com/NateScarlet/auto-derby


for the pluggins themselves it looks like they are custom macros or logic that other users generated or contribuited for the project to run certain events or training for example there are specific pluggins for an uma training in an specific way to get specific results here is the directory in the repo https://github.com/NateScarlet/auto-derby/wiki/Plugins is all in jap so youll need to translate it.

and here are training results posted by other users that used specific pluggins during training https://github.com/NateScarlet/auto-derby/wiki/Nurturing-result
"""

@Rocostre:
fair enough... also if you can at some point you can add the bot to have an optional setting to auto purchase skills based on currect uma stats to compensate and for the current next race, if possible, for example even if you set up priotity skills to buy but when you are about to purchase skills you don have your desired skills bot will look for alternate skills that are availble that will help you on your next race.
im going to try it out with air grove and see what happens

### 0.5.1
vestovia — Yesterday at 7:37
hi! thank you for the umaplay bot, i understand you avoid emulators due to the inherent risk, but just wondering if adb support or support for other emulators is in the plans? im currently using mumuplayer for the 60fps+ as sometimes i play manually and i think it also might allow it to run in the background like uat? though i think i can use rdp for the meantime but it would be nice. thank you again!

EpharGy — 0:11
Any thoughts on making presets more modular? or giving the ability to use a full preset or a modular one?
ie Character, Race Style, Race Length, Other (CM specific or other skills)?
for example, it's pretty tedious to switch out skills for different Styles and CM's

could then mix and match as needed
Maybe not even make predefined modules, but just have it so you can load multiple preset files and it will basically join them,  could leave it up to the user on what details they add in what presets. May need to de-duplicate or look for clashes, or maybe just prioritize based on load order?

add a togle to 'prefer priority stats if are 0.75 less or equal' disabled by default

### 0.5.2
support friend bar when overlapped by support_hint, make sure we don't confuse colors or classification
new library, try to handle autoinstall


Etsuke cures slacker


allow buying in unity cup race day, take skill pts some steps before to have something kind of updated?

adb
## 0.6

### 0.6.0

General:
- Connection error handler (“A connection error occurred”): detect dialog with **white** and **green** buttons; handle “Title Screen” and “Retry”.
- classifier transparent or not? handle transparents, only on main parts like screen detector (lobby)? or simple do multiple clicks when selecting  option in lobby to avoid pressing transparent. WAIT in back and after training

Bot Strategy / Policy:
- Better turn number prediction (11 or 1 for example, fails)
- Final Season: consider turn number on strategy and configuration; avoid Rest on last turn but allow earlier.
- optimization formula as recommended in a paper shared on discord
- For fans goals, we can wait a little more,  like winning maiden, we don't need to take it immediattly we can wait for weak turn add  configuration for this

QoL:
- Adapt Triple Tiara, Crown, and Senior preconfigs for race scheduler
- improvement: show data about support cards: which skills they have, and more, also for trainees. Like gametora

Coach (assistant / helper instead of Auto):
- @Rocostre
"""
As I was experimenting with it, I thought it would be great if, in a future update, you could experiment with an AI coach or something similar. This could involve adding an overlay to the game that provides guidance based on the current preset and its own calculations. Instead of relying solely on an automated bot, it could also offer an option for an overlay assistant to suggest actions.
LLM?
"""


Bot Strategy:
- Rest and recreation during Summer Camp now cures bad conditions
- Resting now has a chance to cure the Night owl and skit outbreak
- You can cure slow metabolism by doing some training


check that support bar is intersecting the support box, otherwise sometimes is not inside at all
## 0.7

### 0.7.0

General:
- More human like behavior

Bot Strategy:
- Fast mode: like human pre check rainbow buttons / hints, to decide if keep watching options or not. For example if rainbows in 2  tiles then we need to investigate, otherwise we can do a shortcut
- Fans handling for “director training” decisions or similar events.

End2End navigator play:
- Github Issue

- I can't replicate this "@Rosetta:After the bot checks for skills after a hint, it doesn't seem to be able to detect any info on the screen and will always rest regardless of energy value"

## To validate


ADB:
- LDPlayer: bugfix, couldn't scroll through races.
- Adjusted the scroll amount

General Bugfixes:
- Bot was 'trying again' even if option was disabled: now properly ignores "Try again". Thanks for reporting: https://github.com/Magody/Umaplay/issues/75 @DominicS48
- Unity Cup bug, was not recognizing gold buttons / race day buttons: Added "Pixel 2 XL" Unity Cup images to YOLO model training dataset: https://github.com/Magody/Umaplay/issues/76 @Boshido (@Dorasu?)
- If was didn't buy a skill, it was not returning to the train screen: Added better control for this https://github.com/Magody/Umaplay/issues/77 @lfmnovaes (Luisao)
- try again keeps failing (when enabled and when disabled)

Skill buying:
- @Only: I do get a lot of [skills] skipping 'Medium Straightaways ◎' grade='◎' (already purchased) when it is still ○ [1/2] . Now properly handle in memory if we buy twice, once per grade. OCR still can't detect the symbol so relying in memory
- @Rosetta/@Unknown: increased confidence from 0.75 to 0.85, and added positive/negative tokens for more skills like 'ABC corners/straightaway'  'frenzied ABC', 'Subdued ...', 'Flustered ...' 'Hesitant ...' etc

Events:
- Added card 30063-ikuno-dictus
- Added characters 102801-hishi-akebono, 101901-agnes-digital

Bot Strategy (URA):
- Adjusted risk for URA, was overcalculating dynamic risk


### 0.4.2

Team Trials automation:
- Solved Bug where it loops on the 'race go' screen

Smart Falcon:
- was losing all careers if no junior race win 'Pre-op or above' goal condition now supported

