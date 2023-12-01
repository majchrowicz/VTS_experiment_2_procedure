### BHT+VTS EXPERIMENT ###
# by Bartosz Majchrowicz, majchrowicz.b@gmail.com

# Set experiment's directory
# working_directory = 'C:/Users/barto/Psych/Badania/PdB Exp2 IB/PythonExperiment' # development laptop
working_directory = 'C:/Users/user/Desktop/B/PythonExperiment' # ZPS lab

# Imports
from psychopy import visual, event, logging, core, data, logging, gui, prefs
from psychopy.sound.backend_ptb import SoundPTB
import numpy as np 
import pandas as pd
import os, random, sys

# prefs.hardware['audioDevice'] = 1
prefs.hardware['audioLib'] = ['ptb', 'pyo','pygame']; # sound.audioLib # to check if PTB is used
prefs.hardware['audioLatencyMode0'] = 3 # def 3
from psychopy import sound # must import the sound module AFTER setting the preferences

os.chdir(working_directory) # ensure relative paths start from the same directory as this script
random.seed(1)

# Session information
testing_mode = 1            # 1 for full experiment length, 0 for quick development (affects subject info, sections inclusion, nr of trials)

if testing_mode == 0:  
    dummy_subj      = 1     # 1 to skip subject details while developing
    screen_mode     = 1     # 1 for full-res secondary screen, 0 for small primary screen
    training_ib     = 1     # 1 to include IB intervals training, 0 to exclude
    training_vts    = 0     # 1 to include VTS training, 0 to exclude
    training_bht    = 0     # 1 to include BHT training, 0 to exclude
    run_bht         = 0     # 1 to include BHT procedure
    run_vts         = 1     # 1 to include VTS procedure 
    run_explicit    = 0     # 1 to include questionnaires
    log_durations   = 1     # 1 to log experiment durations
elif testing_mode == 1: 
    dummy_subj      = 0     # 1 to skip subject details while developing
    screen_mode     = 1     # 1 for full-res secondary screen, 0 for small primary screen
    training_ib     = 1     # 1 to include IB intervals training, 0 to exclude
    training_vts    = 1     # 1 to include VTS training, 0 to exclude
    training_bht    = 1     # 1 to include BHT training, 0 to exclude
    run_bht         = 1     # 1 to include BHT procedure
    run_vts         = 1     # 1 to include VTS procedure 
    run_explicit    = 1     # 1 to include questionnaires
    log_durations   = 1     # 1 to log experiment durations

# Number of trials
if testing_mode == 0:
    # BHT
    nr_of_trials_per_problem            = 2 # def 12
    nr_of_problems                      = 2 # def 6
    nr_of_training_trials_per_problem   = 2 # def 4
    nr_of_max_training_problems         = 3 # def 3 (but can finish earlier)
    # VTS
    nr_of_vts_trials_per_block          = 5 # def 72 (max 99 due to dalays array limit)
    nr_of_vts_blocks                    = 2 # def 3 
    nr_of_vts_trials_per_training_block = 2 # def ?? 9? 
    nr_of_vts_training_blocks           = 2 # def 2 (1st w/o IB, 2nd w/ IB) 
    nr_of_vts_trials_refam              = 2 # def 6
elif testing_mode == 1: 
    # BHT
    nr_of_trials_per_problem            = 12 # def 12
    nr_of_problems                      = 6 # def 6
    nr_of_training_trials_per_problem   = 4 # def 4
    nr_of_max_training_problems         = 3 # def 3 (but can finish earlier)
    # VTS
    nr_of_vts_trials_per_block          = 72 # def 72 (max 99 due to dalays array limit)
    nr_of_vts_blocks                    = 3 # def 3 
    nr_of_vts_trials_per_training_block = 9 # def ?? 9? 
    nr_of_vts_training_blocks           = 2 # def 2 (1st w/o IB, 2nd w/ IB) 
    nr_of_vts_trials_refam              = 6 # def 6

# Prepare participants
if dummy_subj:
    participant = 101
    cb          = 1 # cb 1 left hand location task, right shape
    age         = 999
    sex         = '?'
    condition   = 1 # 0 no control, 1 full control
else: # proper gui input
    info_box = gui.Dlg(title="Info")
    info_box.addField('Numer:')
    info_box.addField('Wiek:')
    info_box.addField('Płeć:', choices=["[wybierz]", "Kobieta", "Mężczyzna", "Inna"])
    info_data = info_box.show()  # show dialog and wait for OK or Cancel
    if info_data[0] == '' or info_data[1] == '' or info_data[2] == '[wybierz]':
        print('>>> Uzupełnij dane! <<<') # missing data
        sys.exit()
    elif any(char.isalpha() for char in info_data[0]) == True or any(char.isalpha() for char in info_data[1]) == True: 
        print('>>> Podaj wartość liczbową dla numeru i/lub wieku! <<<') # non-numeric values
        sys.exit()
    participant = int(info_data[0])
    age = int(info_data[1])
    sex = info_data[2]
    cb_div = np.mod(participant,4) 
    if cb_div == 0 or cb_div == 1:   cb = 1 # left hand location task, right shape
    elif cb_div == 2 or cb_div == 3: cb = 2 # left hand shape task, right location
    condition = np.mod(participant,2)  # 0 no control, 1 full control
exp_date = data.getDateStr()

expInfo = { # expInfo structure
    'participant' : participant,
    'condition'   : condition,
    'cb'          : cb,
    'date'        : exp_date,
    'exp_name'    : 'BHT_VTS',
    'training_bht': training_bht,
    'training_vts': training_vts,
    'trial_nr'    : 0,
    'enable_ib'   : 0
}

# Prepare data logging 
filename = working_directory + os.sep + u'data' + os.sep + '%s_%s' % (expInfo['participant'], expInfo['date']) # data file name stem = absolute path + name
if not os.path.exists('data'):
    os.mkdir('data')
# save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP) # log to the file, for main experiment only
logging.console.setLevel(logging.WARNING)  # log to the console
print('Sound driver: ' + sound.audioLib + '\nSound class: ' + str(sound.Sound)) # check what sound driver is used

### SETUP ###

# Timings (in seconds)
# IB
ib_max_resp     = 7   # def 7
# BHT
stim_dur        = 2.5 # def 2.5
bht_max_resp    = 3   # def 3; max rt for BHT response
fb_sound_dur    = 0.1 # def 0.1
ib_rating_delay = 0.5 # def 0.5; feedback-rating delay 
bht_fin_fb_dur  = 3   # def 3
# VTS
grid_dur        = 0.5 # def 0.5
vts_stim_dur    = 1.5 # def 1.5
vts_max_resp    = 3   # def 3; max rt for VTS response
# Other
max_int_tr_dur  = 2 # def 120; max intervals training per stage
max_break_dur   = 60  # def 60; max break time (BHT and VTS)

# Feedback delays for IB
fb_dels = np.array([0.3, 0.6, 0.9]) # possible feedback delays
shuffled_dels = [] # empty list to hold the shuffled arrays
range_dels_vts = int(np.ceil(99/9)) # shuffling made in batches of 9 trials
for _ in range(range_dels_vts): # replicate, shuffle, and append array N times
    replicated_and_shuffled = np.tile(fb_dels, 3) # replicate 3 delays x 3 times (so we get batches of 9 trials)
    np.random.shuffle(replicated_and_shuffled)
    shuffled_dels.append(replicated_and_shuffled)
fb_dels_array = np.concatenate(shuffled_dels) # concatenate the shuffled arrays to get a final array of feedback delays

# Keys 
key_map = {'left'  : 'd', 
            'right': 'k',
            'esc'  : 'escape'}
action_keys = [key_map['left'], 
               key_map['right'], 
            ['esc']]
leftKeys=   ['1','d']
rightKeys = ['2','k']
acceptKeys= ['space', 'enter']
vts_left_keys = ['w','d','lalt']
vts_right_keys= ['o','k','ralt']
vts_keys = vts_left_keys + vts_right_keys + ['escape']

if cb == 1: # left hand location task, right shape
    loc_keys   = ['w','d','lalt']
    shape_keys = ['o','k','ralt']
elif cb == 2: # left hand shape task, right location
    loc_keys   = ['o','k','ralt']
    shape_keys = ['w','d','lalt']

intervals_keys = ['1', '3', '5', '7', '9']

# Data variables
bht_trial_vars = [  # main data per BHT trial
    'participant',
    'condition',
    'cb', 
    'date',
    'exp_name',
    'frame_rate',
    'training_bht', # 1 training, 0 main experiment
    'enable_ib',
    'trial_nr',
    'problem_nr',
    'action',       # 0 absent, 1 present, 8 premature, 9 too late
    'premature',    # 1 if response while stimuli still on screen
    'response',     # response key (resp)
    'correct_resp', # q for left, p for right
    'correct',      # 0 for incorrect, 1 for correct
    'rt',
    'fb_delay',
    'fb_delay_index', # index of a delay chosen from array of delays
    'ib_estimation',
    'ib_rt',
    'ib_start',
]

bht_problem_vars = [ # additional data per BHT problem
    'participant',
    'condition',
    'cb', 
    'date',
    'training_bht',
    'problem_nr',
    'bht_estimation',
    'bht_rt',
    'bht_start',
    'bht_final_correct',
]

explicit_vars = [ # additional data for explicit ratings 
    'participant','condition','cb', 'ratings',
    'agef1_rating','agef2_rating','agef3_rating','agef4_rating','agef1_rt','agef2_rt','agef3_rt','agef4_rt',
    'nasa1_rating','nasa2_rating','nasa3_rating','nasa4_rating','nasa1_rt','nasa2_rt','nasa3_rt','nasa4_rt'
]

vts_trial_vars = [ # main data per VTS trial
    'participant',
    'condition',
    'cb', 
    'date',
    'exp_name',
    'frame_rate',
    'training_vts', # 0 absent
    'enable_ib',
    'trial_nr',
    'block_nr',
    'stim',
    'action',       # 0 absent, 1 present, 8 premature, 9 too late
    'premature',    # 1 if response while stimuli still on screen
    'response',     # response key (resp)
    'correct_resp', # correct key
    'correct',      # 0 for incorrect, 1 for correct
    'task_sel',     # 1 for locaction, 2 for shape
    'rt',
    'fb_delay',
    'fb_delay_index', # index of a delay chosen from array of delays
    'ib_estimation',
    'ib_rt',
    'ib_start',
]

# Set colours
txt_color = (.3, .3, .3) # grey
bg_color = (-1, -1, -1) # black

# Setup the window
if screen_mode == 0: # for development
    screen_size = [1200,800]; screen_fullscr = False; screen_nr = 0
elif screen_mode == 1: # main experiment
    screen_size = []; screen_fullscr = True; screen_nr = 1
win = visual.Window(
    size=screen_size, fullscr=screen_fullscr, screen=screen_nr,
    allowGUI=True, allowStencil=False,
    monitor='testMonitor',
    color=bg_color,
    colorSpace='rgb',
    blendMode='avg', useFBO=True,
    units='height')
expInfo['frame_rate'] = win.getActualFrameRate()

# Text and instructions
font_size = 0.025
fix_text = visual.TextStim(win=win, text='+', height=.04, pos=(0, 0), color=txt_color)
premature_text = visual.TextStim(win, text="Przedwczesna reakcja!", height=font_size, color=txt_color) 
correct_text = visual.TextStim(win=win, text='Tak', height=font_size, pos=(0, 0), color=txt_color)
incorrect_text = visual.TextStim(win=win, text='Nie', height=font_size, pos=(0, 0), color=txt_color)
no_resp_text = visual.TextStim(win=win, text='Decyduj szybciej!', height=font_size, pos=(0, 0), color=txt_color)
ib_rating_text = visual.TextStim(win, text="Oszacuj opóźnienie", height=font_size, color=txt_color)
no_ib_text = visual.TextStim(win=win, text='Oceniaj szybciej!', height=font_size, pos=(0, 0), color=txt_color)
training_note_text = visual.TextStim(win, text="Trening", pos=(0, -0.2), height=font_size, color=txt_color) 

intro_1_text = visual.TextStim(win, text=open("instructions/intro_1.txt", "r").read(), height=font_size, color=txt_color)
intro_2_text = visual.TextStim(win, text=open("instructions/intro_2.txt", "r").read(), height=font_size, color=txt_color)
intro_3_text = visual.TextStim(win, text=open("instructions/intro_3.txt", "r").read(), height=font_size, color=txt_color)
bye_text = visual.TextStim(win, text="Koniec badania!\nZgłoś się do osoby prowadzącej.\n\nDziękujemy za udział.", height=font_size, color=txt_color) 
debrief_1 = visual.TextStim(win, text=open("instructions/debrief_1.txt", "r").read(), height=font_size, color=txt_color)

# BHT specific
with open('instructions/bht_final_solution.txt', 'r') as file: 
    final_solution_text = file.read()
final_solution_text = visual.TextStim(win, text=final_solution_text, color=txt_color, height=font_size) 
bht_rating_text = visual.TextStim(win, text="Wybierz rozwiązanie", height=font_size, color=txt_color)
end_bht_training_text = visual.TextStim(win, text=open("instructions/bht_end_training.txt", "r").read(), height=font_size, color=txt_color)
instr_bht_training_1 = visual.TextStim(win, text=open("instructions/bht_training_1.txt", "r").read(), height=font_size, color=txt_color) # ansi coding
instr_bht_training_2 = visual.TextStim(win, text=open("instructions/bht_training_2.txt", "r").read(), height=font_size, color=txt_color)
instr_bht_training_repeat = visual.TextStim(win, text=open("instructions/bht_training_repeat.txt", "r").read(), height=font_size, color=txt_color)

# VTS specific
instr_vts_intro = visual.TextStim(win, text=open("instructions/vts_intro.txt", "r").read(), height=font_size, color=txt_color)
instr_vts_refam_1 = visual.TextStim(win, text=open("instructions/vts_refam_1.txt", "r").read(), height=font_size, color=txt_color)
instr_vts_training_1 = visual.TextStim(win, text=open("instructions/vts_training_1.txt", "r").read(), pos = (0,0), height=font_size, color=txt_color)
if cb == 1: # left hand location task, right shape
    instr_vts_training_2 = visual.TextStim(win, text=open("instructions/vts_training_2_cb1.txt", "r").read(), pos = (0,0.11),height=font_size, color=txt_color)
    instr_vts_pic = visual.ImageStim(win, image='instructions/vts_cb1_s.png', pos=(0,-0.27), interpolate=True)
elif cb == 2:
    instr_vts_training_2 = visual.TextStim(win, text=open("instructions/vts_training_2_cb2.txt", "r").read(), pos = (0,0.11), height=font_size, color=txt_color)
    instr_vts_pic = visual.ImageStim(win, image='instructions/vts_cb2_s.png', pos=(0,-0.27), interpolate=True)
instr_vts_training_3 = visual.TextStim(win, text=open("instructions/vts_training_3.txt", "r").read(), pos = (0,0), height=font_size, color=txt_color)

instr_vts_training_ib = visual.TextStim(win, text=open("instructions/vts_training_ib.txt", "r").read(), height=font_size, color=txt_color) 
next_block_text = visual.TextStim(win, text="Następny blok", height=font_size, color=txt_color)
next_block_timed_text = visual.TextStim(win, text=open("instructions/next_block_timed.txt", "r").read(), pos = (0,0.11), height=font_size, color=txt_color) 
end_vts_training_text = visual.TextStim(win, text=open("instructions/vts_end_training.txt", "r").read(), height=font_size, color=txt_color)
end_vts_refam_text = visual.TextStim(win, text=open("instructions/vts_end_refam.txt", "r").read(), pos = (0.04,0), height=font_size, color=txt_color)

# intervals training
intervals_text_intro = visual.TextStim(win, text=open("instructions/intervals_intro.txt", "r").read(), height=font_size, color=txt_color)
intervals_text_1 = visual.TextStim(win, text=open("instructions/intervals_1.txt", "r").read(), height=font_size, color=txt_color)
intervals_text_2 = visual.TextStim(win, text=open("instructions/intervals_2.txt", "r").read(), height=font_size, color=txt_color)
intervals_prompt_0 = visual.TextStim(win, text="Gdy będziesz gotowy/a naciśnij Enter, aby przejść do kolejnej części treningu.", height=font_size, color=txt_color)
intervals_prompt_1 = visual.TextStim(win, text="Naciśnij Spację, aby odtworzyć dźwięk", height=font_size, color=txt_color)
intervals_prompt_2 = visual.TextStim(win, text="Naciśnij Spację, aby odtworzyć dźwięk\nlub Enter, aby zakończyć trening", 
                                     height=font_size, color=txt_color)
txt="Oszacuj opóźnienie między naciśnięciem klawisza\na usłyszeniem dźwięku.\n\nPrzesuwaj wskaźnik klaiwszami D i K,\nzatwierdź wybór Spacją."
ib_rating_text_intervals = visual.TextStim(win, text=txt, height=font_size, color=txt_color)
intervals_end_timed = visual.TextStim(win, text="Upłynął czas tej części treningu. Rozpoczyna się kolejna...", height=font_size, color=txt_color)

# explicit scales
explicit_text = visual.TextStim(win, text=open("instructions/explicit_scales.txt", "r").read(), height=font_size, color=txt_color)

# Sounds
sound_volume = 0.05 # volume, quiet 0.005, def 0.05
correct_sound = SoundPTB(value=800, stereo=True, volume=sound_volume, secs=fb_sound_dur)
incorrect_sound = SoundPTB(value=400, stereo=True, volume=sound_volume*1.1, secs=fb_sound_dur)
neutral_sound = SoundPTB(value=600, stereo=True, volume=sound_volume*1.05, secs=fb_sound_dur) 

# Clocks
trial_clock = core.Clock() # for RTs
training_clock = core.Clock() # whole training session: durations + VTS + BHT
explicit1_clock = core.Clock()
explicit2_clock = core.Clock()
bht_clock = core.Clock() # clean BHT (without training)
vts_clock = core.Clock() # clean VTS (without training and refamiliarization)
total_clock = core.Clock() # total experiment time

### BHT ###

# BHT solutions
bht_solutions = {'training1': 9,
                 'training2': 9, 
                 'training3': 9, # single repeated training problem
                 'problem1' : 6,
                 'problem2' : 1,
                 'problem3' : 7,
                 'problem4' : 10, # 0 in the orginal scale
                 'problem5' : 3,
                 'problem6' : 8}

# BHT trial 
def do_bht_trial(win, expInfo):
    if training_bht == 1:
        stims_path = working_directory + '/BHT_problems/training' + str(expInfo['problem_nr']) + '.xlsx'
    elif training_bht == 0:
        stims_path = working_directory + '/BHT_problems/problem' + str(expInfo['problem_nr']) + '.xlsx'
    stims_bht = pd.read_excel(stims_path)
    # adjust stimuli horizontal position based on its size
    if stims_bht.loc[expInfo['trial_nr']]['ImagesLeft'].split("images/")[1].split("_")[0] == 'large': 
        left_stim_pos = (-0.06,0)
    elif stims_bht.loc[expInfo['trial_nr']]['ImagesLeft'].split("images/")[1].split("_")[0] == 'small': 
        left_stim_pos = (-0.05,0)
    if stims_bht.loc[expInfo['trial_nr']]['ImagesRight'].split("images/")[1].split("_")[0] == 'large': 
        right_stim_pos = (0.06,0)
    elif stims_bht.loc[expInfo['trial_nr']]['ImagesRight'].split("images/")[1].split("_")[0] == 'small': 
        right_stim_pos = (0.05,0)
    stim_left = visual.ImageStim(win, image=stims_bht.loc[expInfo['trial_nr']]['ImagesLeft'], pos=left_stim_pos, interpolate=True, size=0.08)
    stim_right= visual.ImageStim(win, image=stims_bht.loc[expInfo['trial_nr']]['ImagesRight'], pos=right_stim_pos, interpolate=True, size=0.08)
    correct_resp = stims_bht.loc[expInfo['trial_nr']]['CorrAns']
  
    # pick feedback delay from already construed array of possible delays
    if expInfo['problem_nr'] == 1:
        fb_delay_index = expInfo['trial_nr']
        fb_delay = fb_dels_array[fb_delay_index]
    else:
        fb_delay_index = expInfo['trial_nr'] + (nr_of_trials_per_problem * (expInfo['problem_nr']-1))
        fb_delay = fb_dels_array[fb_delay_index]
    
    ib_rating_start_point = random.randint(2,8)
    ib_rating_scale = visual.RatingScale(
        win, low=1, high=10, markerStart=ib_rating_start_point, marker = 'triangle', 
        textColor = txt_color, lineColor = txt_color, textSize = 0.65,
        precision=1, scale=None, size = 0.9, stretch = 1.15, noMouse = True, showAccept = False, 
        labels = ['100','200','300','400','500','600','700','800','900', '1000'],
        tickMarks = ['1','2','3','4','5','6','7','8','9', '10'],
        pos = (0, -0.2), markerColor = [255,255,0], minTime = 0.1, maxTime = ib_max_resp,
        leftKeys=['d'], rightKeys = ['k'], acceptKeys=['space'], respKeys = None)
    
    # set some training dependencies
    if training_bht == 1:
        trial_stimuli = [stim_left, stim_right, fix_text, training_note_text] # set stimuli
    elif training_bht == 0:
        trial_stimuli = [stim_left, stim_right, fix_text] # set stimuli
        expInfo['enable_ib'] = 1 # enable IB ratings
        if condition == 0:
            no_control_fb = stims_bht.loc[expInfo['trial_nr']]['Feedback']

    action, rt, correct = -1, -1, -1 # dummy values
    expInfo['ib_estimation'], expInfo['ib_rt'], expInfo['ib_start'] = -1, -1, -1
    premature = 0 # flag premature responses

    # start trial
    win.flip() 
    for s in trial_stimuli: # draw stimuli (two figures and fixation)
        s.draw()
    win.callOnFlip(trial_clock.reset) # clock will be reset exactly when stimuli will be drawn
    win.flip()

    resp = event.waitKeys(keyList=action_keys, maxWait=stim_dur) # monitor premature keypresses
    if resp: # premature response while stimuli are still on the screen
        if 'escape' in resp:
            core.quit()
        premature_text.draw()
        win.flip()
        action = 8
        premature = 1
        rt = trial_clock.getTime()
        core.wait(1)

    if not premature:
        fix_text.draw() # clear and fixate after stimuli
        win.flip()

        resp = event.waitKeys(keyList=action_keys, maxWait=bht_max_resp) # monitor proper keypresses
        if resp:
            rt = trial_clock.getTime()
            if 'escape' in resp:
                core.quit()
            else:
                action = 1
                core.wait(fb_delay)
                if condition == 1 or training_bht == 1: # full control: feedback depends on response
                    if correct_resp in resp:
                        correct = 1
                        fb_sound = correct_sound
                        # correct_text.draw()
                    else:
                        correct = 0
                        fb_sound = incorrect_sound
                        # incorrect_text.draw()
                elif condition == 0 and training_bht == 0: # no control: feedback fixed, non-contingent
                    if no_control_fb == 'tak': 
                        correct = 1
                        fb_sound = correct_sound
                        # correct_text.draw()
                    elif no_control_fb == 'nie':
                        correct = 0
                        fb_sound = incorrect_sound
                        # incorrect_text.draw()
                fb_sound.play()
                # win.flip()
                core.wait(ib_rating_delay)
                fb_sound.stop()

                # interval estimation (IB rating scale)
                if expInfo['enable_ib'] == 1:
                    event.clearEvents()
                    while ib_rating_scale.noResponse:  # show & update until a response has been made
                        ib_rating_text.draw()
                        ib_rating_scale.draw()
                        win.flip()
                        if event.getKeys(['escape']):
                            core.quit()
                    if ib_rating_scale.getRT() > ib_max_resp:
                        no_ib_text.draw()
                        win.flip()
                        core.wait(0.5)
                        ib_rt = 999
                    else:
                        ib_rt = ib_rating_scale.getRT()
                    expInfo['ib_estimation'] = ib_rating_scale.getRating()
                    expInfo['ib_rt'] = ib_rt
                    expInfo['ib_start'] = ib_rating_start_point

        elif resp is None: # no L/R response
            action = 0
            correct = 9
            resp = '?'
            action = 9
            no_resp_text.draw()
            win.flip()
            core.wait(0.5) 
        core.wait(ib_rating_delay) # sound duration

    expInfo['action'] = action
    expInfo['premature'] = premature
    expInfo['response'] = resp[0]
    expInfo['correct_resp'] = correct_resp
    expInfo['correct'] = correct
    expInfo['rt'] = rt
    expInfo['fb_delay'] = fb_delay
    expInfo['fb_delay_index'] = fb_delay_index

    return expInfo

# BHT problem 
def do_bht_problem(win, expInfo, trials_per_problem):

    bht_rating_start_point = random.randint(2,8)
    bht_rating_scale = visual.RatingScale(
        win, low=1, high=10, markerStart=bht_rating_start_point, marker = 'triangle', 
        textColor = txt_color, lineColor = txt_color, textSize = 0.65,
        precision=1, scale=None, size = 0.9, stretch = 2, noMouse = True, showAccept = False, 
        labels = ['wpisane\n\'R\'','wpisane\n\'r\'','rozmiar\nduży','rozmiar\nmały','kształt\nkwadrat','kształt\ntrójkąt',
                    'strona\nlewa','strona\nprawa','wnętrze\npuste','wnętrze\nkreski'],
        tickMarks = ['1','2','3','4','5','6','7','8','9','10'],
        pos = (0, -0.2), markerColor = [0,255,255], minTime = 0.3,
        leftKeys=['d'], rightKeys = ['k'], acceptKeys=['space'], respKeys = None)
    
    # core.wait(0.2)
    if training_bht == 0:
        next_problem_text = visual.TextStim(win, text='Zadanie ' + str(expInfo['problem_nr']) + ' z ' + str(nr_of_problems), 
                                            height=font_size, color=txt_color)
        next_problem_text.draw()
        win.flip()
        if expInfo['problem_nr'] == 1: core.wait(1.5)
        else: core.wait(3)
        
    # do trial
    for i in range(trials_per_problem):
        expInfo = do_bht_trial(win, expInfo)
        # log trial-level data
        dataline_bht = ';'.join([str(expInfo[var]) for var in bht_trial_vars])
        datafile_bht.write(dataline_bht + '\n')
        datafile_bht.flush()
        expInfo['trial_nr'] += 1

    # final answer (problem solution)
    while bht_rating_scale.noResponse:  # show & update until a response has been made
        bht_rating_text.draw()
        bht_rating_scale.draw()
        win.flip()
        if event.getKeys(['escape']):
            core.quit()
    win.flip()
    core.wait(0.1)
    if condition == 0 and training_bht == 0: # no control and main session
        bht_final_correct = -1
        incorrect_text.draw()
    elif condition == 1 or training_bht == 1: # full control or training session
        if training_bht == 1:
            solution_str = 'training' + str(expInfo['problem_nr'])
        elif training_bht == 0:
            solution_str = 'problem' + str(expInfo['problem_nr'])
        solution = bht_solutions[solution_str]
        if solution == bht_rating_scale.getRating():
            bht_final_correct = 1
            correct_text.draw()
        elif solution != bht_rating_scale.getRating():
            bht_final_correct = 0
            incorrect_text.draw()
    win.flip()
    core.wait(bht_fin_fb_dur) # final answer feedback

    expInfo['trial_nr'] = 0 # reset trial nr (as they enumerate per block)
    expInfo['bht_estimation'] = bht_rating_scale.getRating()
    expInfo['bht_rt'] = bht_rating_scale.getRT()
    expInfo['bht_start'] = bht_rating_start_point
    expInfo['bht_final_correct'] = bht_final_correct

    win.flip()
    # core.wait(0.2)
    # if training_bht == 0:
    #     if expInfo['problem_nr'] < nr_of_problems:
    #         next_problem_text = visual.TextStim(win, text='Zadanie ' + str(expInfo['problem_nr']) + ' z ' + str(nr_of_problems), 
    #                                             height=font_size, color=txt_color)
    #         next_problem_text.draw()
    #         win.flip()
    #     core.wait(1.5)

    return expInfo

### EXPLICIT SCALES ###
def do_explicit_scales(win, expInfo):
    
    explicit_text.draw() # info text
    win.flip()
    event.waitKeys(keyList=acceptKeys)
    marker_color = [169,169,169]

    # Agency and effort 
    agef_labs_1 = ['1\nbardzo małym', '2\nmałym','3\ndość małym','4\nśrednim','5\ndość dużym','6\ndużym','7\nbardzo dużym']
    agef_labs_2 = ['1\nbardzo mało', '2\nmało','3\ndość mało','4\nśrednio','5\ndość dużo','6\ndużo','7\nbardzo dużo']
    agef_marks = ['1','2','3','4','5','6','7']

    agef_text_i1 = visual.TextStim(win, text='W jakim stopniu miałeś/miałaś poczucie kontroli nad efektami zadania?', 
                                color=txt_color, height=0.053, units='norm', wrapWidth = 1.5, pos=(0,.8)) 
    agef_scale_i1 = visual.RatingScale(
        win, low=1, high=7, markerStart=None, marker = 'triangle', singleClick = True, mouseOnly = True,
        textColor = txt_color, lineColor = txt_color, textSize = 0.6,
        precision=1, scale=None, size = 0.9, stretch = 1.25, noMouse = False, showAccept = False, 
        labels = agef_labs_1, tickMarks = agef_marks, markerColor = marker_color,
        pos = (0,.65), acceptKeys=['space', 'enter'])

    agef_text_i2 = visual.TextStim(win, text='W jakim stopniu efekty zadania były dla Ciebie przewidywalne?', 
                                color=txt_color, height=0.053, units='norm', wrapWidth = 1.5, pos=(0,.35)) 
    agef_scale_i2 = visual.RatingScale(
        win, low=1, high=7, markerStart=None, marker = 'triangle', singleClick = True, mouseOnly = True,
        textColor = txt_color, lineColor = txt_color, textSize = 0.6,
        precision=1, scale=None, size = 0.9, stretch = 1.25, noMouse = False, showAccept = False, 
        labels = agef_labs_1, tickMarks = agef_marks, markerColor = marker_color,
        pos = (0, .2), acceptKeys=['space', 'enter'])

    agef_text_i3 = visual.TextStim(win, text='Jak dużo wysiłku umysłowego wymagało dla Ciebie zadanie?', 
                                color=txt_color, height=0.053, units='norm', wrapWidth = 1.5, pos=(0,-.1)) 
    agef_scale_i3 = visual.RatingScale(
        win, low=1, high=7, markerStart=None, marker = 'triangle', singleClick = True, mouseOnly = True,
        textColor = txt_color, lineColor = txt_color, textSize = 0.6,
        precision=1, scale=None, size = 0.9, stretch = 1.25, noMouse = False, showAccept = False, 
        labels = agef_labs_2, tickMarks = agef_marks, markerColor = marker_color,
        pos = (0, -0.25), acceptKeys=['space', 'enter'])

    agef_text_i4 = visual.TextStim(win, text='Jak dużo wysiłku umysłowego włożyłeś/włożyłaś w zadanie?', 
                                color=txt_color, height=0.053, units='norm', wrapWidth = 1.5, pos=(0,-.55)) 
    agef_scale_i4 = visual.RatingScale(
        win, low=1, high=7, markerStart=None, marker = 'triangle', singleClick = True, mouseOnly = True,
        textColor = txt_color, lineColor = txt_color, textSize = 0.6,
        precision=1, scale=None, size = 0.9, stretch = 1.25, noMouse = False, showAccept = False, 
        labels = agef_labs_2, tickMarks = agef_marks, markerColor = marker_color,
        pos = (0, -.7), acceptKeys=['space', 'enter'])

    agef_elements = [agef_text_i1, agef_scale_i1, agef_text_i2, agef_scale_i2, agef_text_i3, agef_scale_i3, agef_text_i4, agef_scale_i4]

    event.Mouse(visible=True, newPos=(0,0.45)) # set mouse position on top
    while agef_scale_i1.noResponse or agef_scale_i2.noResponse or agef_scale_i3.noResponse or agef_scale_i4.noResponse: # show&update until response 
        for el in agef_elements: el.draw()
        win.flip()
        if event.getKeys(['escape']): core.quit()

    agef1_rating = agef_scale_i1.getRating(); agef2_rating = agef_scale_i2.getRating(); 
    agef3_rating = agef_scale_i3.getRating(); agef4_rating = agef_scale_i4.getRating()
    agef1_rt = agef_scale_i1.getRT(); agef2_rt = agef_scale_i2.getRT(); 
    agef3_rt = agef_scale_i3.getRT(); agef4_rt = agef_scale_i4.getRT()
    
    # NASA 
    nasa_labels = ['1\nbardzo małe', '2\n','3\n','4\n','5\n','6\n','7\nbardzo duże']
    nasa_marks = ['1','2','3','4','5','6','7']

    nasa_text_i1 = visual.TextStim(win, text='Jak duże było obciążenie umysłowe podczas wykonywania zadania?', 
                                color=txt_color, height=0.053, units='norm', wrapWidth = 1.5, pos=(0,.8)) 
    nasa_scale_i1 = visual.RatingScale(
        win, low=1, high=7, markerStart=None, marker = 'triangle', singleClick = True, mouseOnly = True,
        textColor = txt_color, lineColor = txt_color, textSize = 0.65,
        precision=1, scale=None, size = 0.9, stretch = 1, noMouse = False, showAccept = False, 
        labels = nasa_labels, tickMarks = nasa_marks, markerColor = marker_color,
        pos = (0,.65), 
        acceptKeys=['space', 'enter'])

    nasa_text_i2 = visual.TextStim(win, text='Jak duże było obciążenie fizyczne podczas wykonywania zadania?', 
                                color=txt_color, height=0.053, units='norm', wrapWidth = 1.5, pos=(0,.35)) 
    nasa_scale_i2 = visual.RatingScale(
        win, low=1, high=7, markerStart=None, marker = 'triangle', singleClick = True, mouseOnly = True,
        textColor = txt_color, lineColor = txt_color, textSize = 0.65,
        precision=1, scale=None, size = 0.9, stretch = 1, noMouse = False, showAccept = False, 
        labels = nasa_labels, tickMarks = nasa_marks, markerColor = marker_color,
        pos = (0, .2), 
        acceptKeys=['space', 'enter'])

    nasa_text_i3 = visual.TextStim(win, text='Jak dużego pośpiechu wymagało wykonywanie zadania?', 
                                color=txt_color, height=0.053, units='norm', wrapWidth = 1.5, pos=(0,-.1)) 
    nasa_scale_i3 = visual.RatingScale(
        win, low=1, high=7, markerStart=None, marker = 'triangle', singleClick = True, mouseOnly = True,
        textColor = txt_color, lineColor = txt_color, textSize = 0.65,
        precision=1, scale=None, size = 0.9, stretch = 1, noMouse = False, showAccept = False, 
        labels = nasa_labels, tickMarks = nasa_marks, markerColor = marker_color,
        pos = (0, -0.25), 
        acceptKeys=['space', 'enter'])

    nasa_text_i4 = visual.TextStim(win, text='Jak duży wysiłek musiałeś/aś włożyć w wykonanie zadania,\nżeby osiągnąć taki efekt, jaki uzyskałeś/aś?', 
                                color=txt_color, height=0.053, units='norm', wrapWidth = 1.5, pos=(0,-.55)) 
    nasa_scale_i4 = visual.RatingScale(
        win, low=1, high=7, markerStart=None, marker = 'triangle', singleClick = True, mouseOnly = True,
        textColor = txt_color, lineColor = txt_color, textSize = 0.65,
        precision=1, scale=None, size = 0.9, stretch = 1, noMouse = False, showAccept = False, 
        labels = nasa_labels, tickMarks = nasa_marks, markerColor = marker_color,
        pos = (0, -.7), 
        acceptKeys=['space', 'enter'])

    nasa_elements = [nasa_text_i1, nasa_scale_i1, nasa_text_i2, nasa_scale_i2, nasa_text_i3, nasa_scale_i3, nasa_text_i4, nasa_scale_i4]

    event.Mouse(visible=True, newPos=(0,0.45)) # set mouse position on top
    while nasa_scale_i1.noResponse or nasa_scale_i2.noResponse or nasa_scale_i3.noResponse or nasa_scale_i4.noResponse: # show&update until response
        for el in nasa_elements: el.draw()
        win.flip()
        if event.getKeys(['escape']): core.quit()

    nasa1_rating = nasa_scale_i1.getRating(); nasa2_rating = nasa_scale_i2.getRating(); 
    nasa3_rating = nasa_scale_i3.getRating(); nasa4_rating = nasa_scale_i4.getRating()
    nasa1_rt = nasa_scale_i1.getRT(); nasa2_rt = nasa_scale_i2.getRT(); 
    nasa3_rt = nasa_scale_i3.getRT(); nasa4_rt = nasa_scale_i4.getRT()
  
    # Log ratings and RTs
    expInfo['agef1_rating'] = agef1_rating; expInfo['agef2_rating'] = agef2_rating
    expInfo['agef3_rating'] = agef3_rating; expInfo['agef4_rating'] = agef4_rating
    expInfo['agef1_rt'] = agef1_rt; expInfo['agef2_rt'] = agef2_rt
    expInfo['agef3_rt'] = agef3_rt; expInfo['agef4_rt'] = agef4_rt 
    expInfo['nasa1_rating'] = nasa1_rating; expInfo['nasa2_rating'] = nasa2_rating
    expInfo['nasa3_rating'] = nasa3_rating; expInfo['nasa4_rating'] = nasa4_rating
    expInfo['nasa1_rt'] = nasa1_rt; expInfo['nasa2_rt'] = nasa2_rt
    expInfo['nasa3_rt'] = nasa3_rt; expInfo['nasa4_rt'] = nasa4_rt 

    return expInfo

### VTS ###

stims_vts = pd.read_excel(working_directory + '/vts_stimuli.xlsx')
stims_indices = np.random.randint(low = 0, high = len(stims_vts), 
                                  size = nr_of_vts_trials_per_block) # vector of stimuli indices to be used throughout the trials

# VTS trial 
def do_vts_trial(win, expInfo):
    grid = visual.ImageStim(win, image='vts_images/grid.png')
    stim = visual.ImageStim(win, image=stims_vts.Stimuli[stims_indices[expInfo['trial_nr']]]) # nr of trial used as index for stimuli list
    grid.size *= 0.15; stim.size *= 0.15 # scale to remain aspect ratio
    stimulus = stims_vts.Stimuli[stims_indices[expInfo['trial_nr']]].split('vts_images/')[1].split('.png')[0] # get stimulus type from path name
    
    fb_delay = fb_dels_array[expInfo['trial_nr']] # pick feedback delay from already construed array of possible delays
    fb_delay_index = expInfo['trial_nr']

    ib_rating_start_point = random.randint(2,8)
    ib_rating_scale = visual.RatingScale(
        win, low=1, high=10, markerStart=ib_rating_start_point, marker = 'triangle', 
        textColor = txt_color, lineColor = txt_color, textSize = 0.65,
        precision=1, scale=None, size = 0.9, stretch = 1.15, noMouse = True, showAccept = False, 
        labels = ['100','200','300','400','500','600','700','800','900', '1000'],
        tickMarks = ['1','2','3','4','5','6','7','8','9', '10'],
        pos = (0, -0.2), markerColor = [255,255,0], minTime = 0.1, maxTime = ib_max_resp,
        leftKeys=['d'], rightKeys = ['k'], acceptKeys=['space'], respKeys = None)
     
    action, rt, correct = -1, -1, -1 # dummy values
    correct_resp, task_sel = 'NA', -1
    expInfo['ib_estimation'], expInfo['ib_rt'], expInfo['ib_start'] = -1, -1, -1
    premature = 0 # flag premature responses

    # start trial
    grid.draw()
    if expInfo['training_vts'] == 1: training_note_text.draw()
    win.flip()
    core.wait(grid_dur)
    stim.draw()
    if expInfo['training_vts'] == 1: training_note_text.draw()
    win.callOnFlip(trial_clock.reset) # clock will be reset exactly when stimuli will be drawn
    win.flip()

    resp = event.waitKeys(keyList=vts_keys, maxWait=vts_stim_dur) # monitor premature keypresses
    if resp: # premature response while stimuli are still on the screen
        if 'escape' in resp:
                action = 9
                core.quit()
        premature_text.draw()
        win.flip()
        action = 8
        premature = 1
        rt = trial_clock.getTime()
        core.wait(1)

    if not premature:
        grid.draw() # clear grid after stimuli
        win.flip()

        resp = event.waitKeys(keyList=vts_keys, maxWait=vts_max_resp) # monitor proper keypresses
        if resp:
            rt = trial_clock.getTime()
            if 'escape' in resp:
                action = 9
                core.quit()
            else:
                action = 1
                core.wait(fb_delay)
                if cb == 1: # left hand location task
                    if resp[0] in vts_left_keys: 
                        correct_resp = stims_vts.correct_loc_left[stims_indices[expInfo['trial_nr']]]
                        if resp[0] == correct_resp:
                            correct = 1
                            fb_sound = correct_sound
                        else: 
                            correct = 0
                            fb_sound = incorrect_sound
                        task_sel = 1 # location
                    elif resp[0] in vts_right_keys:  
                        correct_resp = stims_vts.correct_shape_right[stims_indices[expInfo['trial_nr']]]
                        if resp[0] == correct_resp:
                            correct = 1
                            fb_sound = correct_sound
                        else: 
                            correct = 0
                            fb_sound = incorrect_sound
                        task_sel = 2 # shape
                elif cb == 2: # left hand shape taks
                    if resp[0] in vts_left_keys: 
                        correct_resp = stims_vts.correct_shape_left[stims_indices[expInfo['trial_nr']]]
                        if resp[0] == correct_resp:
                            correct = 1
                            fb_sound = correct_sound
                        else: 
                            correct = 0
                            fb_sound = incorrect_sound
                        task_sel = 2 # shape
                    elif resp[0] in vts_right_keys:  
                        correct_resp = stims_vts.correct_loc_right[stims_indices[expInfo['trial_nr']]]
                        if resp[0] == correct_resp:
                            correct = 1
                            fb_sound = correct_sound
                        else: 
                            correct = 0
                            fb_sound = incorrect_sound
                        task_sel = 1 # location
                    
                fb_sound.play()
                win.flip()
                core.wait(ib_rating_delay)
                fb_sound.stop()

                # interval estimation (IB rating scale)
                if expInfo['enable_ib'] == 1:
                    event.clearEvents()
                    while ib_rating_scale.noResponse:  # show & update until a response has been made
                        ib_rating_text.draw()
                        ib_rating_scale.draw()
                        win.flip()
                        if event.getKeys(['escape']):
                            core.quit()
                    if ib_rating_scale.getRT() > ib_max_resp:
                        no_ib_text.draw()
                        win.flip()
                        core.wait(0.5)
                        ib_rt = 999
                    else:
                        ib_rt = ib_rating_scale.getRT()
                    expInfo['ib_estimation'] = ib_rating_scale.getRating()
                    expInfo['ib_rt'] = ib_rt
                    expInfo['ib_start'] = ib_rating_start_point

        elif resp is None: # no L/R response
            action = 0
            correct = 9
            resp = '?'
            action = 9
            no_resp_text.draw()
            win.flip()
            core.wait(0.5) 
        core.wait(ib_rating_delay) # sound duration
                
    expInfo['stim'] = stimulus
    expInfo['action'] = action
    expInfo['premature'] = premature
    expInfo['response'] = resp[0]
    expInfo['correct_resp'] = correct_resp
    expInfo['correct'] = correct
    expInfo['task_sel'] = task_sel
    expInfo['rt'] = rt
    expInfo['fb_delay'] = fb_delay
    expInfo['fb_delay_index'] = fb_delay_index

    return expInfo

# VTS block

def do_vts_block(win, expInfo, nr_of_vts_trials_per_block):

    for i in range(nr_of_vts_trials_per_block):
        expInfo = do_vts_trial(win, expInfo)
        
        # log trial-level data
        dataline_vts = ';'.join([str(expInfo[var]) for var in vts_trial_vars])
        datafile_vts.write(dataline_vts + '\n')
        datafile_vts.flush()
        expInfo['trial_nr'] += 1
        
    expInfo['trial_nr'] = 0 # reset trial nr (as they enumerate per block)
    
    win.flip()
    core.wait(0.3)
    if training_vts == 0:
        if expInfo['block_nr'] < nr_of_vts_blocks:
            next_block_timed_text.draw()
            instr_vts_pic.draw()
            win.flip()
            event.waitKeys(keyList=acceptKeys, maxWait = max_break_dur) # max wait
    
    return expInfo

### INTERVALS TRAINING ###

def intervals_training(win, expInfo):
    
    intervals_for_training = [.7, .1, .5, .9, .3, .1, .5] # pre-defined ordered intervals (recycled if needed)
       
    # Stage 1: try known intervals
    intervals_text_intro.draw()
    win.flip()
    event.waitKeys(keyList=acceptKeys)
    
    intervals_clock = core.Clock() 
    cont = 0
    i = 0  # initialize the loop counter
    while cont == 0:
        event.clearEvents()
        intervals_text_1.draw()
        if i > 8: # add info about finishing training after several trials
            intervals_prompt_0.pos = (0,-.31)
            intervals_prompt_0.draw()
        win.flip()
        
        resp = event.waitKeys(keyList = ['1','2','3','4','5','6','7','8','9','0','return'], maxWait= max_int_tr_dur)
        if resp != ['return']:
            if resp == ['1']:   core.wait(0.1)
            elif resp == ['2']: core.wait(0.2)
            elif resp == ['3']: core.wait(0.3)
            elif resp == ['4']: core.wait(0.4)
            elif resp == ['5']: core.wait(0.5)
            elif resp == ['6']: core.wait(0.6)
            elif resp == ['7']: core.wait(0.7)
            elif resp == ['8']: core.wait(0.8)
            elif resp == ['9']: core.wait(0.9)
            elif resp == ['0']: core.wait(1)
            neutral_sound.play()
            core.wait(fb_sound_dur)
            neutral_sound.stop()      
            i += 1  # increment the loop counter
        elif resp == ['return']:
            cont = 1
        elif 'escape' in resp: core.quit()
        
        if intervals_clock.getTime() > max_int_tr_dur: # terminate stage if max training time is reached 
            intervals_end_timed.draw()
            win.flip()
            cont = 1
            core.wait(2.5)
       
    # Stage 2: estimate intervals on the scale
    intervals_text_2.draw()
    win.flip()
    event.waitKeys(keyList=acceptKeys)
      
    intervals_clock.reset()  
    cont = 0
    i = 0  # initialize the loop counter
    while cont == 0:
        event.clearEvents()    
        ib_rating_scale = visual.RatingScale(
            win, low=1, high=10, markerStart=random.randint(2,8), marker = 'triangle', 
            textColor = txt_color, lineColor = txt_color, textSize = 0.65,
            precision=1, scale=None, size = 0.9, stretch = 1.15, noMouse = True, showAccept = False, 
            labels = ['100','200','300','400','500','600','700','800','900', '1000'],
            tickMarks = ['1','2','3','4','5','6','7','8','9', '10'],
            pos = (0, -0.3), markerColor = [255,255,0],
            leftKeys=['d'], rightKeys = ['k'], acceptKeys=['space'], respKeys = None)
        
        if i <= 6:
            intervals_prompt_1.draw()
        else: # add info about finishing training after several trials
            intervals_prompt_2.draw()
        win.flip()
        resp = event.waitKeys(keyList = ['space','return','escape'], maxWait= max_int_tr_dur)
        if 'space' in resp:
            interval_idx = intervals_for_training[i % len(intervals_for_training)] # modulo to wrap the index when max length of array is reached
            core.wait(interval_idx)
            neutral_sound.play()
            core.wait(fb_sound_dur)
            neutral_sound.stop()
            while ib_rating_scale.noResponse:  # show & update until a response has been made
                ib_rating_text_intervals.draw()
                ib_rating_scale.draw()
                win.flip()
                if event.getKeys(['escape']):
                    core.quit()
            ib_rating_scale.reset()
            i += 1  # increment the loop counter
        elif 'return' in resp:
            cont = 1
        elif 'escape' in resp: core.quit()
        
        if intervals_clock.getTime() > max_int_tr_dur: # terminate stage if max training time is reached 
            intervals_end_timed.draw()
            win.flip()
            cont = 1
            core.wait(2.5)

### EXECUTE ###

# Init data files
if run_bht == 1:
    datafile_bht = open(filename+'_bht.csv', 'w') # BHT trial-level file
    datafile_bht.write(';'.join(bht_trial_vars) + '\n')
    datafile_bht.flush()
    datafile_problem = open(filename+'_problem.csv', 'w') # BHT problem-level file
    datafile_problem.write(';'.join(bht_problem_vars) + '\n')
    datafile_problem.flush()
if run_explicit == 1:
    datafile_explicit = open(filename+'_explicit.csv', 'w') # explicit ratings file
    datafile_explicit.write(';'.join(explicit_vars) + '\n')
    datafile_explicit.flush()
if run_vts == 1:
    datafile_vts = open(filename+'_vts.csv', 'w') # VTS trial-level file
    datafile_vts.write(';'.join(vts_trial_vars) + '\n')
    datafile_vts.flush()

# Reset clocks
training_clock.reset()
total_clock.reset()

# Start instructions
intro_1_text.draw()
win.flip()
event.waitKeys(keyList=acceptKeys)
intro_2_text.draw()
win.flip()
event.waitKeys(keyList=acceptKeys)
intro_3_text.draw()
win.flip()
event.waitKeys(keyList=acceptKeys)

# Intervals training
if training_ib == 1:
    intervals_training(win, expInfo)
    
# VTS training
if run_vts == 1 and training_vts == 1: # training session
    instr_vts_intro.draw()
    win.flip()
    event.waitKeys(keyList=acceptKeys)

    for n in range(nr_of_vts_training_blocks):
        if n == 0:
            expInfo['enable_ib'] = 0
            # 1st instructions
            instr_vts_training_1.draw()
            win.flip()
            event.waitKeys(keyList=acceptKeys)
            # 2nd
            instr_vts_pic.draw()
            instr_vts_training_2.draw()
            win.flip()
            event.waitKeys(keyList=acceptKeys)
            # 3rd
            instr_vts_pic.draw()
            instr_vts_training_3.draw()
            win.flip()
            event.waitKeys(keyList=acceptKeys)
        elif n == 1:
            expInfo['enable_ib'] = 1
            instr_vts_pic.draw()
            instr_vts_training_ib.pos = (0,0.1)
            instr_vts_training_ib.draw()
            win.flip()
            event.waitKeys(keyList=acceptKeys)
            
        expInfo['block_nr'] = n+1
        expInfo = do_vts_block(win, expInfo, nr_of_vts_trials_per_training_block)
      
    trial_nr = 0 # finish training      

# BHT training and main
if run_bht == 1:
    expInfo['enable_ib'] = 1
    if training_bht == 1: # training session
        
        cont = 0 
        while cont == 0:
            for n in range(nr_of_max_training_problems):
                if n == 0:
                    # instructions
                    instr_bht_training_1.draw()
                    win.flip()
                    event.waitKeys(keyList=acceptKeys)
                    instr_bht_training_2.draw()
                    win.flip()
                    event.waitKeys(keyList=acceptKeys)

                expInfo['problem_nr'] = n+1
                expInfo = do_bht_problem(win, expInfo, trials_per_problem = nr_of_training_trials_per_problem)

                # log problem-level data
                dataline_problem = ';'.join([str(expInfo[var]) for var in bht_problem_vars])
                datafile_problem.write(dataline_problem + '\n')
                datafile_problem.flush()
                
                # ask if repeat or finish training
                if n < nr_of_max_training_problems-1:
                    instr_bht_training_repeat.draw()
                    win.flip()
                    resp = event.waitKeys(keyList = intervals_keys + ['return', 'space', 'escape'])
                    if resp == ['return']:
                        cont = 1
                        break
                    elif 'escape' in resp: core.quit()
            cont = 1

        training_bht, trial_nr = 0, 0 # finish training
        end_bht_training_text.draw()
        win.flip()
        event.waitKeys(keyList=acceptKeys)
        
    training_dur = training_clock.getTime() # get duration of training
    expInfo['problem_nr'], expInfo['trial_nr'], expInfo['training_bht'], expInfo['enable_ib'] = 0, 0, 0, 1 
    bht_clock.reset() # reset after training

    # if training_bht == 0: # main session
    for n in range(nr_of_problems):
        expInfo['problem_nr'] = n+1
        expInfo = do_bht_problem(win, expInfo, trials_per_problem = nr_of_trials_per_problem)

        # log problem-level data
        dataline_problem = ';'.join([str(expInfo[var]) for var in bht_problem_vars])
        datafile_problem.write(dataline_problem + '\n')
        datafile_problem.flush()
    
    bht_dur = bht_clock.getTime() # get duration of BHT

# Explicit scales #1
if run_explicit == 1:
    explicit1_clock.reset()
    expInfo['ratings'] = 'bht'
    do_explicit_scales(win, expInfo)
    explicit1_dur = explicit1_clock.getTime()
    # log explicit data
    dataline_explicit = ';'.join([str(expInfo[var]) for var in explicit_vars])
    datafile_explicit.write(dataline_explicit + '\n')
    datafile_explicit.flush()

# VTS refamiliarization and main
if run_vts == 1: 
    if training_vts == 1: # refamiliarization session
        instr_vts_refam_1.pos = (0,0.15)
        instr_vts_refam_1.draw()
        instr_vts_pic.draw()
        win.flip()
        event.waitKeys(keyList=acceptKeys)
        
        # only 1 refamiliarization block (no loop)
        expInfo['block_nr'] = 3 # increase nr in relation to first training blocks
        expInfo = do_vts_block(win, expInfo, nr_of_vts_trials_refam)
                
    training_vts, trial_nr = 0, 0 # finish refamiliarization
    instr_vts_pic.draw()
    end_vts_refam_text.pos = (0,0.15)
    end_vts_refam_text.draw()
    win.flip()
    event.waitKeys(keyList=acceptKeys)
        
    expInfo['block_nr'], expInfo['trial_nr'], expInfo['training_vts'], expInfo['enable_ib'] = 0, 0, 0, 1 
    vts_clock.reset() # reset after training
    
    for n in range(nr_of_vts_blocks): # main session
        if n > 0:
            next_block_text.draw()
            win.flip()
            core.wait(3)
            
        expInfo['block_nr'] = n+1
        expInfo = do_vts_block(win, expInfo, nr_of_vts_trials_per_block)
    vts_dur = vts_clock.getTime()
                
# Explicit scales #2
if run_explicit == 1:
    explicit2_clock.reset()
    expInfo['ratings'] = 'vts'
    do_explicit_scales(win, expInfo)
    explicit2_dur = explicit2_clock.getTime()
    # log explicit data
    dataline_explicit = ';'.join([str(expInfo[var]) for var in explicit_vars])
    datafile_explicit.write(dataline_explicit + '\n')
    datafile_explicit.flush()

# Finish
total_dur = total_clock.getTime() # get total experiment time
if log_durations == 1: # log durations data
    dur_names = ['participant', 'exp_date']
    durs = [participant, exp_date]
    if run_bht:
        dur_names.append('training')
        durs.append(training_dur)
    if run_explicit:
        dur_names.append('explicit1')
        durs.append(explicit1_dur)
    if run_bht:
        dur_names.append('bht')
        durs.append(bht_dur)
    if run_explicit:
        dur_names.append('explicit2')
        durs.append(explicit2_dur)
    if run_vts:
        dur_names.append('vts')
        durs.append(vts_dur)
    dur_names.append('total')
    durs.append(total_dur)
    
    durs_df = pd.DataFrame([dur_names, durs]) # create data frame using pandas
    durs_df.to_csv(filename+'_durations.csv', index=False, header=False, sep=';') # export to csv
        
debrief_1.draw()
win.flip()
event.waitKeys(keyList=acceptKeys)
core.quit()