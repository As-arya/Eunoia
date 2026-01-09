"""Seed Screening Questions - PHQ-9/GAD-7 Evidence-Based"""
from app.extensions import db
from app.models import ScreeningQuestion, AnswerOption

def update_religious_text():
    """Update any religious text in existing database to neutral alternatives"""
    # Update answer options
    religious_updates = [
        ('Alhamdulillah, baik! 😊', 'Luar biasa baik! 😊'),
    ]
    for old_text, new_text in religious_updates:
        option = AnswerOption.query.filter(AnswerOption.option_text == old_text).first()
        if option:
            option.option_text = new_text
            db.session.commit()
            print(f"✓ Updated: '{old_text}' -> '{new_text}'")

def seed_questions():
    if ScreeningQuestion.query.first():
        return
    
    # Evidence-based screening questions adapted from PHQ-9 and GAD-7
    questions = [
        # Opening - Rapport Building
        ('Opening', 'Hai! Aku senang bisa berbicara denganmu. Bagaimana perasaanmu saat ini?', [
            ('Luar biasa baik! 😊', 0, 'Happy'),
            ('Biasa saja', 1, 'Neutral'),
            ('Kurang baik...', 2, 'Sad'),
            ('Sangat tidak baik', 3, 'Distressed')
        ]),
        
        # PHQ-9 Item 1 - Anhedonia
        ('Depression', 'Dalam 2 minggu terakhir, seberapa sering kamu merasa minat atau kesenangan berkurang dalam melakukan sesuatu?', [
            ('Tidak pernah', 0, 'Stable'),
            ('Beberapa hari', 1, 'Neutral'),
            ('Lebih dari setengah waktu', 2, 'Low'),
            ('Hampir setiap hari', 3, 'Depressed')
        ]),
        
        # PHQ-9 Item 2 - Depressed Mood
        ('Depression', 'Seberapa sering kamu merasa down, sedih, atau putus asa?', [
            ('Tidak pernah', 0, 'Stable'),
            ('Beberapa hari', 1, 'Occasionally_sad'),
            ('Lebih dari setengah waktu', 2, 'Sad'),
            ('Hampir setiap hari', 3, 'Depressed')
        ]),
        
        # PHQ-9 Item 3 - Sleep
        ('Sleep', 'Bagaimana dengan tidurmu? Apakah kamu kesulitan tidur, atau justru tidur terlalu banyak?', [
            ('Tidur normal', 0, 'Rested'),
            ('Kadang susah tidur', 1, 'Tired'),
            ('Sering bermasalah', 2, 'Exhausted'),
            ('Hampir selalu bermasalah', 3, 'Severely_fatigued')
        ]),
        
        # PHQ-9 Item 4 - Fatigue
        ('Energy', 'Seberapa sering kamu merasa lelah atau kehilangan energi?', [
            ('Energi baik', 0, 'Energetic'),
            ('Kadang lelah', 1, 'Tired'),
            ('Sering lelah', 2, 'Fatigued'),
            ('Selalu lelah', 3, 'Exhausted')
        ]),
        
        # PHQ-9 Item 6 - Guilt/Worthlessness
        ('Self', 'Apakah kamu pernah merasa buruk tentang dirimu sendiri, atau merasa telah mengecewakan diri sendiri atau keluarga?', [
            ('Tidak', 0, 'Confident'),
            ('Kadang-kadang', 1, 'Self_doubt'),
            ('Sering', 2, 'Guilty'),
            ('Hampir selalu', 3, 'Worthless')
        ]),
        
        # PHQ-9 Item 7 - Concentration
        ('Focus', 'Apakah kamu kesulitan berkonsentrasi pada hal-hal seperti membaca, menonton, atau bekerja?', [
            ('Tidak ada masalah', 0, 'Focused'),
            ('Kadang sulit', 1, 'Distracted'),
            ('Sering sulit', 2, 'Unfocused'),
            ('Hampir tidak bisa konsentrasi', 3, 'Scattered')
        ]),
        
        # GAD-7 Item 1 - Nervousness
        ('Anxiety', 'Seberapa sering kamu merasa nervous, cemas, atau was-was?', [
            ('Tidak pernah', 0, 'Calm'),
            ('Beberapa hari', 1, 'Occasionally_anxious'),
            ('Lebih dari setengah waktu', 2, 'Anxious'),
            ('Hampir setiap hari', 3, 'Severely_anxious')
        ]),
        
        # GAD-7 Item 2 - Uncontrollable Worry
        ('Anxiety', 'Apakah kamu tidak bisa menghentikan atau mengontrol kekhawatiranmu?', [
            ('Tidak', 0, 'Controlled'),
            ('Kadang', 1, 'Somewhat_worried'),
            ('Sering', 2, 'Worried'),
            ('Hampir selalu', 3, 'Overwhelmed_by_worry')
        ]),
        
        # GAD-7 Item 4 - Trouble Relaxing
        ('Anxiety', 'Seberapa sulit bagimu untuk rileks?', [
            ('Mudah rileks', 0, 'Relaxed'),
            ('Agak sulit', 1, 'Tense'),
            ('Sulit', 2, 'Very_tense'),
            ('Sangat sulit/tidak bisa', 3, 'Cannot_relax')
        ]),
        
        # GAD-7 Item 6 - Irritability  
        ('Anxiety', 'Apakah kamu mudah merasa kesal atau irritable?', [
            ('Tidak', 0, 'Even_tempered'),
            ('Kadang', 1, 'Occasionally_irritable'),
            ('Sering', 2, 'Irritable'),
            ('Hampir selalu', 3, 'Very_irritable')
        ]),
        
        # Stress Assessment
        ('Stress', 'Ketika menghadapi tekanan, bagaimana biasanya kamu mengatasinya?', [
            ('Bisa mengelola dengan baik', 0, 'Calm'),
            ('Berusaha mencari cara', 1, 'Neutral'),
            ('Sering merasa kewalahan', 2, 'Stress'),
            ('Sangat sulit mengatasinya', 3, 'Overwhelmed')
        ]),
        
        # Social Support (Protective Factor)
        ('Social', 'Apakah kamu merasa memiliki seseorang yang bisa kamu ajak bicara ketika kesulitan?', [
            ('Ya, banyak', 0, 'Supported'),
            ('Ya, ada beberapa', 1, 'Somewhat_supported'),
            ('Hanya satu atau dua orang', 2, 'Limited_support'),
            ('Tidak ada', 3, 'Isolated')
        ]),
        
        # Functional Impairment
        ('Functional', 'Seberapa sulit masalah-masalah ini membuat kamu menjalankan pekerjaan atau bergaul dengan orang lain?', [
            ('Tidak sulit sama sekali', 0, 'Functional'),
            ('Agak sulit', 1, 'Mild_difficulty'),
            ('Sangat sulit', 2, 'Moderate_difficulty'),
            ('Extremely sulit', 3, 'Severe_difficulty')
        ]),
        
        # Closing - Help Seeking
        ('Closing', 'Terakhir, apakah kamu tertarik untuk berbicara dengan profesional kesehatan mental?', [
            ('Ya, saya ingin', 0, 'Open'),
            ('Mungkin, masih ragu', 1, 'Ambivalent'),
            ('Belum siap', 2, 'Resistant'),
            ('Tidak perlu', 3, 'Dismissive')
        ]),
        
        # Additional PHQ-9 Items
        ('Depression', 'Apakah nafsu makanmu berubah akhir-akhir ini (makan terlalu sedikit atau terlalu banyak)?', [
            ('Normal', 0, 'Stable'),
            ('Sedikit berubah', 1, 'Neutral'),
            ('Cukup berubah', 2, 'Affected'),
            ('Sangat berubah', 3, 'Disturbed')
        ]),
        
        ('Depression', 'Apakah kamu merasa sulit mengambil keputusan atau berpikir jernih?', [
            ('Tidak', 0, 'Clear'),
            ('Kadang', 1, 'Neutral'),
            ('Sering', 2, 'Foggy'),
            ('Hampir selalu', 3, 'Confused')
        ]),
        
        # Additional Energy/Physical
        ('Energy', 'Apakah kamu merasa gerakan atau bicaramu melambat, atau sebaliknya lebih gelisah?', [
            ('Normal', 0, 'Balanced'),
            ('Sedikit', 1, 'Neutral'),
            ('Cukup terasa', 2, 'Affected'),
            ('Sangat terasa', 3, 'Severely_affected')
        ]),
        
        ('Sleep', 'Apakah kamu sering terbangun di tengah malam dan sulit tidur kembali?', [
            ('Tidak pernah', 0, 'Rested'),
            ('Jarang', 1, 'Neutral'),
            ('Sering', 2, 'Disturbed_sleep'),
            ('Hampir setiap malam', 3, 'Insomnia')
        ]),
        
        # Additional Anxiety
        ('Anxiety', 'Apakah kamu sering merasa seolah akan terjadi sesuatu yang buruk?', [
            ('Tidak', 0, 'Calm'),
            ('Kadang', 1, 'Uneasy'),
            ('Sering', 2, 'Anxious'),
            ('Hampir selalu', 3, 'Catastrophizing')
        ]),
        
        ('Anxiety', 'Apakah kamu mengalami gejala fisik seperti jantung berdebar, keringat berlebih, atau gemetar saat cemas?', [
            ('Tidak', 0, 'Calm'),
            ('Kadang', 1, 'Mild_symptoms'),
            ('Sering', 2, 'Moderate_symptoms'),
            ('Hampir selalu', 3, 'Severe_symptoms')
        ]),
        
        # Additional Stress
        ('Stress', 'Apakah kamu merasa waktu tidak pernah cukup untuk menyelesaikan tugas-tugasmu?', [
            ('Tidak', 0, 'Managed'),
            ('Kadang', 1, 'Sometimes_busy'),
            ('Sering', 2, 'Stressed'),
            ('Hampir selalu', 3, 'Overwhelmed')
        ]),
        
        ('Stress', 'Bagaimana hubunganmu dengan orang-orang terdekat akhir-akhir ini?', [
            ('Baik', 0, 'Connected'),
            ('Agak tegang', 1, 'Strained'),
            ('Cukup bermasalah', 2, 'Conflicted'),
            ('Sangat bermasalah', 3, 'Isolated')
        ]),
        
        # Social/Support
        ('Social', 'Apakah kamu merasa kesepian meskipun dikelilingi orang?', [
            ('Tidak', 0, 'Connected'),
            ('Kadang', 1, 'Occasionally_lonely'),
            ('Sering', 2, 'Lonely'),
            ('Hampir selalu', 3, 'Very_lonely')
        ]),
        
        ('Social', 'Seberapa sering kamu menghindari aktivitas sosial karena perasaanmu?', [
            ('Tidak pernah', 0, 'Social'),
            ('Kadang', 1, 'Occasionally_avoiding'),
            ('Sering', 2, 'Avoiding'),
            ('Hampir selalu', 3, 'Withdrawn')
        ]),
        
        # Self/Coping
        ('Self', 'Apakah kamu memiliki aktivitas yang membuatmu merasa tenang dan bahagia?', [
            ('Ya, banyak', 0, 'Resourceful'),
            ('Ya, beberapa', 1, 'Coping'),
            ('Sedikit', 2, 'Limited_coping'),
            ('Tidak ada', 3, 'No_coping')
        ]),
        
        ('Self', 'Bagaimana kamu menilai kemampuanmu untuk bangkit dari situasi sulit?', [
            ('Sangat baik', 0, 'Resilient'),
            ('Cukup baik', 1, 'Moderate_resilience'),
            ('Kurang baik', 2, 'Low_resilience'),
            ('Sangat buruk', 3, 'Not_resilient')
        ]),
        
        # Focus/Work
        ('Focus', 'Apakah pekerjaanmu atau studimu terpengaruh oleh kondisi emosimu?', [
            ('Tidak', 0, 'Productive'),
            ('Sedikit', 1, 'Mildly_affected'),
            ('Cukup', 2, 'Affected'),
            ('Sangat', 3, 'Severely_affected')
        ])
    ]
    
    for i, (cat, text, opts) in enumerate(questions):
        q = ScreeningQuestion(category=cat, question_text=text, order=i+1)
        db.session.add(q)
        db.session.flush()
        for opt_text, val, emotion in opts:
            db.session.add(AnswerOption(question_id=q.id, option_text=opt_text, option_value=val, emotion_tag=emotion))
    
    db.session.commit()
    print(f"✓ Seeded {len(questions)} PHQ-9/GAD-7 based questions")


