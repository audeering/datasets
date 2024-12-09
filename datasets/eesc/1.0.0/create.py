import os
import shutil
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup
import pandas as pd

import audeer
import audformat


def main():
    source_url = 'https://metashare.ut.ee/repository/download/4d42d7a8463411e2a6e4005056b40024a19021a316b54b7fb707757d43d1a889/'
    description = (
        'The establishment of the Estonian Emotional Speech Corpus (EESC) '
        'began in 2006 within the framework of the National Programme '
        'for Estonian Language Technology at the Institute of the Estonian Language. '
        'The corpus contains 1,234 Estonian sentences that '
        'express anger, joy and sadness, or are neutral. '
        'Two female speakers were chosen to read the sentences, and were instructed: '
        'Read the text so that you render its mood. '
        'The text passages chosen were journalistic texts, '
        'unanimously recognised by readers in a special test, to '
        'contain the emotions of joy, anger or sadness. '
        'Listening test subjects heard isolated sentences without seeing the text '
        'and then had to decide which emotion the sentences contained. '
        'The available choices were the three emotions: sadness, anger, '
        'or joy, or neutral speech. '
        'At least 30 Estonians listened to each sentence. '
        'In 908 sentences more than 50% of listeners identified '
        'one and the same emotion, or neutrality. '
        'Additionally, another test was performed where 14 other subjects '
        'had to decide on the emotion or neutrality of each sentence '
        'by reading the text (and not listening to the audio). '
        'Emotions determined by listening or reading only did not always coincide. '
        'Note that the dataset files, transcription, and gold standard emotion labels are '
        'available under a CC-BY-3.0 license, but the additional labels '
        'of speaker information, emotion agreement, and '
        'whether the text matches the emotion, are available at '
        'http://peeter.eki.ee:5000/ without a license.'
    )
    languages = ['et']
    db = audformat.Database(
        name='eesc',
        source=source_url,
        usage=audformat.define.Usage.COMMERCIAL,
        description=description,
        license='CC-BY-3.0',
        languages=languages,
        author=(
            'Rene Altrov, Hille Pajupuu (Institute of the Estonian Language)'
        ),
    )
    current_dir = os.path.dirname(__file__)
    build_dir = audeer.mkdir(os.path.join(current_dir, './build'))
    audio_dir = 'audios'
    audio_path = os.path.join(current_dir, audio_dir)
    audeer.mkdir(audio_path)
    sentence_report_dir = os.path.join(current_dir, 'sentence_reports_emotion')
    emotion_map = {
        "anger": "anger",
        "joy": "happiness",
        "neutral": "neutral",
        "sadness": "sadness",
    }

    df = pd.DataFrame()
    for emotion in emotion_map.keys():
        sentence_report_content = parse_sentence_report_html(
            os.path.join(sentence_report_dir, f'{emotion}_content.html'),
            source_url, audio_path, audio_dir)
        df = pd.concat((df, sentence_report_content))

        sentence_report_no_content = parse_sentence_report_html(
            os.path.join(sentence_report_dir, f'{emotion}_no_content.html'), source_url, audio_path, audio_dir)
        df = pd.concat((df, sentence_report_no_content))

    print(df['speaker'].unique())
    # Speakers are ['Marju 10-11' 'Marju 2' 'Marju 14' 'Marju 6' 'Marju 12-13' 'Marit 3'
    #  'Marju 8-9']
    # Assume that all Marju are the same (sanity checked by listening), and Marit is another speaker
    df['speaker'] = df['speaker'].apply(lambda x: x.split(' ')[0])
    speaker_dict = {
        'Marit': {'gender': 'female', 'language': audformat.utils.map_language('et')},
        'Marju': {'gender': 'female', 'language': audformat.utils.map_language('et')}
    }
    speaker_df = pd.DataFrame.from_dict(speaker_dict, orient='index')
    speaker_df.index.name = 'speaker'
    speaker_df.index = speaker_df.index.astype('string')

    db.schemes['transcription'] = audformat.Scheme(
        dtype='str'
    )
    db.schemes['emotion'] = audformat.Scheme(
        labels={v: {'original': k} for k, v in emotion_map.items()}
    )
    db.schemes['emotion.agreement'] = audformat.Scheme(
        dtype='float', minimum=0, maximum=1
    )
    db.schemes['text-matches-emotion'] = audformat.Scheme(
        dtype='bool', description='Whether the annotations for the audio coincides with the '
                                  'annotations for the text content.'
    )
    db.schemes['gender'] = audformat.Scheme(
        labels=['female', 'male']
    )
    db.schemes['language'] = audformat.Scheme(
        labels=[audformat.utils.map_language(lang) for lang in languages],
        description='The language of the speaker.'
    )
    db['speaker'] = audformat.MiscTable(speaker_df.index)
    db['speaker']['gender'] = audformat.Column(scheme_id='gender')
    db['speaker']['gender'].set(speaker_df['gender'])
    db['speaker']['language'] = audformat.Column(scheme_id='language')
    db['speaker']['language'].set(speaker_df['language'])

    db.schemes['speaker'] = audformat.Scheme(
        labels='speaker', dtype='str'
    )

    db['files'] = audformat.Table(
        index=df.index
    )
    db['files']['speaker'] = audformat.Column(
        scheme_id='speaker'
    )
    db['files']['speaker'].set(df['speaker'])
    db['files']['transcription'] = audformat.Column(
        scheme_id='transcription', description='The sentence the speakers were asked to perform.'
    )
    db['files']['transcription'].set(df['sentence'])
    db.splits['test'] = audformat.Split(type='test', description='The entire dataset is used for testing.')
    db[f'emotion.categories.test.gold_standard'] = audformat.Table(
        index=df.index, split_id='test',
        description=f'The categorical emotions that the majority of the annotators agreed on.'
    )
    db[f'emotion.categories.test.gold_standard']['emotion'] = audformat.Column(
        scheme_id='emotion'
    )
    db[f'emotion.categories.test.gold_standard']['emotion'].set(df['emotion'].map(emotion_map))
    db[f'emotion.categories.test.gold_standard']['emotion.agreement'] = audformat.Column(
        scheme_id='emotion.agreement'
    )
    db[f'emotion.categories.test.gold_standard']['emotion.agreement'].set(
        df['recognition_rate'].apply(lambda x: float(x)/100)
    )
    db[f'emotion.categories.test.gold_standard']['text-matches-emotion'] = audformat.Column(
        scheme_id='text-matches-emotion'
    )
    db[f'emotion.categories.test.gold_standard']['text-matches-emotion'].set(df['content_influence'])
    if not os.path.exists(os.path.join(build_dir, audio_dir)):
        shutil.copytree(
            audio_path,
            os.path.join(build_dir, audio_dir)
        )
    db.save(build_dir)


def parse_sentence_report_html(sentence_report_path, url, audio_path, audio_dir):
    with open(sentence_report_path, 'r') as fp:
        html = fp.read()
    soup = BeautifulSoup(html, features="html.parser")
    items = soup.find_all('div', {'id': 'list'})
    sentences = []
    file_ids = []
    recognition_rates = []
    speakers = []
    files = []
    for item in items:
        recognition_rate = item.find('div', {'class': 'first'}).next
        sentence_item = item.find('div', {'class': 'lasttext'})
        sentence = sentence_item.find('a', {'title': 'Click to listen!'}).next
        sentences.append(sentence)
        recognition_rates.append(recognition_rate)
        file_items = sentence_item.find_all('a', {'class': 'ot'})
        for file_item in file_items:
            if file_item.has_attr('title'):
                # parse id and speaker
                speaker = file_item['title']
                speaker = speaker.split(':')[1].strip()
                speakers.append(speaker)
                file_path = file_item['href']
                file_id = audeer.basename_wo_ext(file_path)
                file_ids.append(file_id)
                # download audio file
                file_url = urllib.parse.urljoin(url, file_path)
                file_save_path = os.path.join(audio_path, os.path.basename(file_path))
                if not os.path.exists(file_save_path):
                    urllib.request.urlretrieve(file_url, file_save_path)
                files.append(os.path.join(audio_dir, os.path.basename(file_path)))
                break
    df = pd.DataFrame({'sentence': sentences, 'recognition_rate': recognition_rates, 'speaker': speakers,
                       'id': file_ids}, index=files)
    filename = os.path.basename(sentence_report_path)
    for emotion in ['anger', 'joy', 'neutral', 'sadness']:
        if filename.startswith(emotion):
            df['emotion'] = emotion
    df['content_influence'] = 'no_content' not in filename
    df.index.name = 'file'
    return df


if __name__ == '__main__':
    main()
