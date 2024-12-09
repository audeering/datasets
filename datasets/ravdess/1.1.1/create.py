import audb
import audeer
import audformat

name = 'ravdess'
previous_version = '1.1.0'
build_dir = '../build'
build_dir = audeer.mkdir(build_dir)

audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
    cache_root=None,
    verbose=True
)
db = audformat.Database.load(build_dir)

original2unified_emotion = {
    'angry': 'anger',
    'calm': 'calm',
    'disgust': 'disgust',
    'fearful': 'fear',
    'happy': 'happiness',
    'neutral': 'neutral',
    'sad': 'sadness',
    'surprised': 'surprise'
}

previous2unified_emotion = {
    'angry': 'anger',
    'calm': 'calm',
    'disgust': 'disgust',
    'fearful': 'fear',
    'happy': 'happiness',
    'neutral': 'neutral',
    'sad': 'sadness',
    'suprised': 'surprise'  # typo in previous version's emotion scheme: suprised is used instead of surprised
}

# new unified scheme, storing the original labels as well
db.schemes['emotion'] = audformat.Scheme(
    labels={unified_emotion: {'original': original} for original, unified_emotion in original2unified_emotion.items()}
)

for split in ['train', 'dev', 'test']:
    for vocal_channel in ['speech', 'song']:
        original_col = db[f'emotion.{vocal_channel}.{split}']['emotion'].get()
        unified_emotion_col = original_col.map(previous2unified_emotion)
        db[f'emotion.{vocal_channel}.{split}']['emotion'] = audformat.Column(scheme_id='emotion')
        db[f'emotion.{vocal_channel}.{split}']['emotion'].set(unified_emotion_col)

db.save(build_dir)
