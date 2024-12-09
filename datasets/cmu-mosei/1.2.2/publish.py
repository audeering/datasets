import audb
import audeer


name = 'cmu-mosei'
previous_version = '1.2.0'
version = '1.2.2'
build_dir = '../build'
repository = audb.repository(name, previous_version)

build_dir = audeer.mkdir(build_dir)

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
)

# Update header metadata
db.license = 'CC-BY-NC-4.0'
db.author = (
    'AmirAli Bagher Zadeh, '
    'Paul Pu Liang, '
    'Soujanya Poria, '
    'Erik Cambria, '
    'Louis-Philippe Morency'
)
db.organization = 'MultiComp Lab, Carnegie Mellon uUiversity '
db.description = (
    'Multimodal Opinion Sentiment and Emotion Intensity Sentiment '
    'and emotion annotated multimodal data '
    'automatically collected from YouTube. '
    'The dataset contains more than 23,500 sentence utterance videos '
    'from more than 1000 online YouTube speakers. '
    'The dataset is gender balanced. '
    'All the sentences utterance are randomly chosen '
    'from various topics and monologue videos. '
    'The videos are transcribed and properly punctuated. '
    'All videos are stated to have a creative commons license '
    'that allows for personal unrestricted use. '
    'The annotations have a different less strict license '
    'and can be used also for commercial applications. '
    'Reference: '
    'http://dx.doi.org/10.18653/v1/P18-1208'
)
db.save(build_dir)

audb.publish(
    build_dir,
    version,
    repository,
    previous_version=previous_version,
)
