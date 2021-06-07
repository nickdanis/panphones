def isolate_segments(game_list):
    '''
    gets individual segments from word list
    OBSOLETE??
    '''
    segments = [seg for word, pron in game_list for seg in pron]
    segments = list(set(segments))
    return segments

def generate_phones(segments):
    '''
    picks 7 random phones, with one of these marked as the center phone
    OBSOLETE
    '''
    phones = random.sample(segments, 7)
    center = random.choice(phones)
    return (phones, center)