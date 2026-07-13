import pytest
import logging

from parsers.article_parser import ArticleParser
from models.models import Translation


@pytest.fixture
def parser():
    obj = ArticleParser()

    obj.logger = logging.getLogger(__name__)

    return obj


def test_basic_article_ra(parser: ArticleParser):
    test_articles_ra = [
        """…ら
…等
суф. мн. числа; после имени собств. и другие; и его друзья (сторонники); и иже с ним, и его присные; и сопровождающие его лица.
"""
    ]

    results = parser.process_results(test_articles_ra)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "…等"
    assert first_res.reading == "…ら"
    assert first_res.mainsense == "суф. мн. числа"


def test_basic_article_hani(parser: ArticleParser):
    test_articles_hani = [
        """はんい
範囲
сфера, область, круг; диапазон; радиус [действий]; предел;
我々の範囲では в нашем кругу;
私の知る範囲では насколько мне известно;
範囲を限る ставить [определённые] рамки чему-л., ограничивать пределы чего-л.;
人智の範囲を越える быть за пределами человеческих знаний;
彼の読書の範囲は広い круг (диапазон) его чтения широк."""
    ]

    results = parser.process_results(test_articles_hani)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "範囲"
    assert first_res.reading == "はんい"
    assert first_res.mainsense == "сфера, область, круг"


def test_basic_article_no(parser: ArticleParser):
    test_articles = [
        """の
野
поле; равнина; луг; степь; степь"""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "野"
    assert first_res.reading == "の"
    assert first_res.mainsense == "поле, равнина, луг, степь"


def test_basic_article_shindan(parser: ArticleParser):
    test_articles = [
        """しんだん
診断
диагноз;
～する, 診断を下す ставить диагноз;
医者には診断がつかなかった врач не мог поставить диагноза."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "診断"
    assert first_res.reading == "しんだん"
    assert first_res.mainsense == "диагноз, ставить диагноз"


def test_basic_article_iu(parser: ArticleParser):
    test_articles = [
        """いう
言う
1. говорить; сказать, заметить; заявлять; излагать; высказывать; утверждать
2. рассказывать, сообщать
3. называть; называться"""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "言う"
    assert first_res.reading == "いう"
    assert first_res.mainsense == "говорить, сказать, заметить"


def test_list_article_beshi(parser: ArticleParser):
    test_articles = [
        """べし
可し
1. нужно, следует (делать и т.п.)
2. должно быть, вероятно"""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "可し"
    assert first_res.reading == "べし"
    assert first_res.mainsense == "нужно, следует (делать и т.п.)"


def test_list_article_tokoro(parser: ArticleParser):
    test_articles = [
        """ところ
所I･処
сущ.
1) место;
…～にある находиться где-л.;
…する所がない негде сделать что-л.;
所かまわず безразлично где (в каком месте), в любом месте;
所によって異なる различаться в зависимости от места (от того, где находится);
彼の行っている所が分からない я не знаю, куда он ушёл (уехал); я не знаю, где он;
人のいる所 в присутствии людей; при людях;
その町は海抜二千フィートの所にある этот город расположен на высоте 2000 футов над уровнем моря;
2) [определённое] место;
所を得る быть на [своём] месте;
物には所がある всему своё место;
3) местожительство; чей-л. дом;
所を教える объяснять, где живёшь, давать свой адрес;
私の所に у меня [дома];
伊東の所に行く пойти к г-ну Ито́;
伊東さんの所のお嬢さん дочь г-на Ито́;
おじの所にいる жить у дяди;
ぼくの所は家族が多い у меня большая семья;
4) перен. место, сторона; черты;
弱い所 слабое место, слабая сторона;
いい所がある есть положительные стороны (моменты);
彼らは見る所が異なる у них разные точки зрения, они смотрят с разных точек зрения;
5) кое-что, что-то; то что;
君の言う所 то, что ты говоришь;
それが私の望む所だ вот чего мне хочется, вот на что я надеюсь;
この事にもっともらしい所もある в этом есть кое-что правдоподобное;
彼は学者らしい所がある в нём есть что-то от учёного;
彼女には女らしい所がない в ней нет ничего женственного;
…は周知の所である что-л. общеизвестно; общеизвестно, что…;
君の知る所ではない это не твоё дело;
私の見た所では по тому, что я видел…; насколько я видел;
私の知っている所で насколько мне известно, насколько я знаю."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "所I･処"
    assert first_res.reading == "ところ"
    assert first_res.mainsense == "место, находиться где-л"


def test_list_article_dzukuri(parser: ArticleParser):
    test_articles = [
        """…づくり
…造り
построенный из чего-л.;
煉瓦造りの кирпичный."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "…造り"
    assert first_res.reading == "…づくり"
    assert first_res.mainsense == "построенный из чего-л"
    assert (
        first_res.senses
        == """построенный из чего-л.;
煉瓦造りの кирпичный."""
    )


def test_list_article_mame(parser: ArticleParser):
    test_articles = [
        """まめ　　　　
まめ･忠実
1): ～な честный, преданный;
まめに勤める честно служить;
2): ～な старательный, усердный;
まめに働く усердно работать;
3): ～な здоровый;
まめである, まめで暮らしている быть здоровым."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "まめ･忠実"
    assert first_res.reading == "まめ"
    assert first_res.mainsense == "честный, преданный"
    assert (
        first_res.senses
        == """1): ～な честный, преданный;
まめに勤める честно служить;
2): ～な старательный, усердный;
まめに働く усердно работать;
3): ～な здоровый;
まめである, まめで暮らしている быть здоровым."""
    )


def test_list_article_jun(parser: ArticleParser):
    test_articles = [
        """じゅん　　　
純
1): ～な чистый, незапятнанный;
2): ～[な] чистый, беспримесный, без примеси."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "純"
    assert first_res.reading == "じゅん"
    assert first_res.mainsense == "чистый, незапятнанный"


def test_date_chouwa(parser: ArticleParser):
    test_articles = [
        """ちょうわ　　
長和
1012.XII — 1017.IV"""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "長和"
    assert first_res.reading == "ちょうわ"
    assert first_res.mainsense == "1012.XII — 1017.IV"
    assert first_res.senses == "1012.XII — 1017.IV"


def test_recursive_articles(parser: ArticleParser):
    test_articles = [
        """つく　　　　
木菟･木兎
см. <<みみずく>>.""",
        """かくしん　　
閣臣
уст. см. <<こくむだいじん>>.""",
        """しゅくし　　
祝詞
кн. см.
1) <<のりと>>;
2) <<しゅくじ>>.""",
        """ルビ　　　　
(англ. ruby)
1) см. <<ルビかつじ>>;
2) см. <<ふりがな>>.""",
    ]

    results = parser.process_results(test_articles)

    assert len(results) == 0


def test_colon_kaikan(parser: ArticleParser):
    test_articles = [
        """かいかん　　
開罐･開缶
: ～する открывать банку (напр. консервов)."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "開罐･開缶"
    assert first_res.reading == "かいかん"
    assert first_res.mainsense == "открывать банку"


def test_colon_shoukei(parser: ArticleParser):
    test_articles = [
        """しょうけい　
小慧
: ～の кн. толковый, смышлёный."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "小慧"
    assert first_res.reading == "しょうけい"
    assert first_res.mainsense == "кн. толковый, смышлёный"


def test_with_footnote_boudai(parser: ArticleParser):
    test_articles = [
        """ぼうだい　　
厖大
неправ. 尨大
: ～な огромный, громадный;
厖大な本 объёмистая книга."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "厖大"
    assert first_res.reading == "ぼうだい"
    assert first_res.mainsense == "огромный, громадный"


def test_nonstandard_kakaru(parser: ArticleParser):
    test_articles = [
        """かかる
как 2-ой компонент сложн. гл. указывает на начало и незаконченность действия:
начинается..., вот-вот..., почти..., чуть не..."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "かかる"
    assert first_res.reading == "かかる"
    assert first_res.mainsense == "начинается..., вот-вот..., почти..., чуть не"


def test_recursive_good(parser: ArticleParser):
    test_articles = [
        """ひざし　　　
日差し･日射し
1) солнечный свет, лучи солнца;
2) см. <<ひあし【日脚】 1>>."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "日差し･日射し"
    assert first_res.reading == "ひざし"
    assert first_res.mainsense == "солнечный свет, лучи солнца"


def test_kata_only(parser: ArticleParser):
    test_articles = [
        """チョコレート
шоколад (англ. chocolate)"""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "チョコレート"
    assert first_res.reading == "チョコレート"
    assert first_res.mainsense == "шоколад"


def test_article_with_brackets(parser: ArticleParser):
    test_articles = [
        """ごう
号
1. номер (порядковый; употр. после числ.)
2. номер (журнала, газеты и т.п.), выпуск
3. параграф; пункт; рубрика (после числ.)
4. псевдоним
5. учёная степень"""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "号"
    assert first_res.reading == "ごう"
    assert first_res.mainsense == "номер порядковый"


def test_article_one_kanji_diff_reading(parser: ArticleParser):
    test_articles = [
        """たん, たんぶ　
反･段, 反歩･段歩
= 10 сэ = 0,0992 га""",
        """はん　　　　
反
1) лог. антитезис;
2) см. <<はんたい【反対】>>;
3) см. <<はんせつ【反切】>>.""",
        """はん　　　　
反…
анти…, контр…, против[о]…;
反帝国主義的 антиимпериалистический.""",
    ]

    result1 = parser.process_results(test_articles)[1]
    result2 = parser.process_results(test_articles)[2]

    assert result1.word == "反"
    assert result1.reading == "はん"
    assert result1.mainsense == "лог. антитезис"
    assert result2.word == "反…"
    assert result2.reading == "はん"
    assert result2.mainsense == "анти…, контр…, против[о]…"


def test_yarxi_simple_article(parser: ArticleParser):
    test_articles = [
        """東口
[higashiguchi]
восточный вход (выход)

TN57062"""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "東口"
    assert result.reading == "ひがしぐち"
    assert result.mainsense == "восточный вход (выход)"
    assert result.senses == "восточный вход (выход)"


def test_godan_second_form_hottarakashi(parser: ArticleParser):
    test_articles = [
        """ほったらかし
2-я основа от:
ほったらかす
放ったらかす
откладывать; забрасывать, бросать; оставлять (без внимания, присмотра)"""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "ほったらかし"
    assert result.reading == "ほったらかし"
    assert result.mainsense == "откладывать"
    assert (
        result.senses
        == """2-я основа от:
ほったらかす
放ったらかす
откладывать; забрасывать, бросать; оставлять (без внимания, присмотра)"""
    )


def test_loanword_mangan(parser: ArticleParser):
    test_articles = [
        """マンガン　　
уст. 満俺
(нем. Mangan) хим. марганец."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "マンガン"
    assert result.reading == "マンガン"
    assert result.mainsense == "хим. марганец"
    assert (
        result.senses
        == """уст. 満俺
(нем. Mangan) хим. марганец."""
    )


def test_loanword_furan(parser: ArticleParser):
    test_articles = [
        """フラン　　　
уст. 法
франк."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "フラン"
    assert result.reading == "フラン"
    assert result.mainsense == "франк"
    assert (
        result.senses
        == """уст. 法
франк."""
    )


def test_onomatopoeia_article_potsuri(parser: ArticleParser):
    test_articles = [
        """ぽつり　　　
ономат.:
ぽつりと一粒雨があたった на меня капнул дождь;
ぽつりと星が一つ残っている на небе видна одинокая звезда."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "ぽつり"
    assert result.reading == "ぽつり"
    assert result.mainsense == "на меня капнул дождь"


def test_onomatopoeia_article_gorogoro(parser: ArticleParser):
    test_articles = [
        """ごろごろ　　
ономат.
1): ごろごろ言う音 грохот, грохотанье, тарахтенье;
ごろごろ喉を鳴らす мурлыкать (о кошке);
腹がごろごろ鳴る в животе урчит;
ごろごろぴかぴか грохочет и сверкает (о громе и молнии);
2): ～する бездельничать, болтаться [без дела] (о ком-л.); валяться [, где не следует] (о чём-л.);
日曜をごろごろ暮らす провести всё воскресенье в безделье;
英語の教師は口が無くて諸方にごろごろしていた из-за отсутствия мест преподаватели английского языка кое-где остались без дела;
◇眼がごろごろする у кого-л. воспалённые глаза."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "ごろごろ"
    assert result.reading == "ごろごろ"
    assert result.mainsense == "грохот, грохотанье, тарахтенье"


def test_nonstandart_article(parser: ArticleParser):
    test_articles = [
        """こころまち　
心待ち
связ.: 心待ちに待つ ждать с нетерпением, ждать не дождаться, быть в страстном ожидани"""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "心待ち"
    assert result.reading == "こころまち"
    assert (
        result.mainsense
        == "ждать с нетерпением, ждать не дождаться, быть в страстном ожидани"
    )


def test_bad_newline_article(parser: ArticleParser):
    test_articles = [
        """てうち　　　
手打ち
1) уст.:
～にする убить самолично (своей собственной рукой);
お手打ちになる(合う) быть убитым своим господином, умереть от меча своего хозяина;
2) заключение сделки;
～にする ударить по рукам;
もう手打ちになりました сделка уже заключена;
3) примирение;
4): ～[の] собственного (ручного) изготовления (о лапше и т. п.)."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "手打ち"
    assert result.reading == "てうち"
    assert result.mainsense == "убить самолично (своей собственной рукой)"


def test_letter_list_article_nanori(parser: ArticleParser):
    test_articles = [
        """なのり　　　
名乗り
: ～をする, 名乗りをあげる а) называть себя, представляться; б) назваться кем-л.;
…の親類の名乗りをする назваться чьим-л. родственником; в) выставлять свою кандидатуру (на выборах и т. п.)."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "名乗り"
    assert result.reading == "なのり"
    assert result.mainsense == "называть себя, представляться"


def test_letter_list_article_tsuki(parser: ArticleParser):
    test_articles = [
        """つき　　　　
付きI
сущ. связ.:
付きが良い а) хорошо сидеть (об одежде); хорошо ложиться (напр. о краске, пудре); не расплываться (о чернилах); хорошо отпечатываться; легко загораться (о топливе); б) быть приятным человеком;
付きの悪い人 несимпатичный человек."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "付きI"
    assert result.reading == "つき"
    assert result.mainsense == "хорошо сидеть (об одежде)"


def test_loanword_centimetre(parser: ArticleParser):
    test_articles = [
        """センチメートル　
уст. 珊
(англ. centimetre) сантиметр."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "センチメートル"
    assert result.reading == "センチメートル"
    assert result.mainsense == "сантиметр"


def test_recursive_yuke(parser: ArticleParser):
    test_articles = [
        """ゆけ　　　　
湯気
связ.: 湯気にあたる почувствовать себя плохо от слишком горячей ванны."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "湯気"
    assert result.reading == "ゆけ"
    assert result.mainsense == "почувствовать себя плохо от слишком горячей ванны"


def test_really_bad_article(parser: ArticleParser):
    test_articles = [
        """カルタ　　　
уст. 歌留多, 加留多, 骨牌
(португ. carta) [игральные] карты;
カルタ一組 колода карт;
カルタをやる(取る) играть в карты;
骨牌を切る тасовать карты."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "カルタ"
    assert result.reading == "カルタ"
    assert result.mainsense == "[игральные] карты"


def test_really_bad_article_hitoshii(parser: ArticleParser):
    test_articles = [
        """ひとしい　　
等しい･均しい･斉しい
равный; одинаковый, такой же;
彼等は年が等しい они одних лет, они одного возраста;
この二つは全然等しい эти две вещи совершенно одинаковы (равны);
等しく分配する распределять поровну;
一里は12.960尺に等しい одно ри равно 12.960 ся́ку;
彼は死人に等しい он всё равно что мёртвый."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "等しい･均しい･斉しい"
    assert result.reading == "ひとしい"
    assert result.mainsense == "равный"


def test_article_with_footnote_chiken(parser: ArticleParser):
    test_articles = [
        """ちけん　　　
地検
(сокр. 地方検事局) районная прокуратура."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "地検"
    assert result.reading == "ちけん"
    assert result.mainsense == "районная прокуратура"


def test_really_bad_article_banzen(parser: ArticleParser):
    test_articles = [
        """ばんぜん　　
万全
связ.:
万全を期するため для полной гарантии, для верности;
～の надёжный, верный; безопасный;
万全の策 все меры; надёжные (эффективные) меры; предусмотрительная политика."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "万全"
    assert result.reading == "ばんぜん"
    assert result.mainsense == "для полной гарантии, для верности"


def test_really_bad_article_sameru(parser: ArticleParser):
    test_articles = [
        """さめる　　　
覚める･醒める
связ.:
[目が]覚める просыпаться, пробуждаться; очнуться;
目がさめている時 когда кто-л. на ногах (не спит);
目のさめるような美人 ослепительная красавица;
迷いがさめる очнуться от иллюзий; раскрыть глаза на что-л.; прийти в себя;
酔いが醒める протрезвиться."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "覚める･醒める"
    assert result.reading == "さめる"
    assert result.mainsense == "просыпаться, пробуждаться"


def test_really_bad_article_ryokai(parser: ArticleParser):
    test_articles = [
        """りょうかい　
了解･諒解I
уст. 領会, 領解
понимание;
～する понимать;
了解し難い непонятный;
了解し得る понятный;
我々の了解する所では насколько мы понимаем."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "了解･諒解I"
    assert result.reading == "りょうかい"
    assert result.mainsense == "понимание, понимать"


def test_really_bad_article_eibun(parser: ArticleParser):
    test_articles = [
        """えいぶん　　
叡聞
связ.: 叡聞に達する довести до сведения императора."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "叡聞"
    assert result.reading == "えいぶん"
    assert result.mainsense == "довести до сведения императора"


def test_really_bad_article_koukaku(parser: ArticleParser):
    test_articles = [
        """こうかく　　
口角
связ.: 口角泡/アワ/を飛ばして с пеной у рта, горячо, страстно (спорить и т. п.)."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "口角"
    assert result.reading == "こうかく"
    assert result.mainsense == "с пеной у рта, горячо, страстно (спорить и т. п.)"


def test_yarxi_simple_article_speedup(parser: ArticleParser):
    test_articles = [
        """スピードアップ
[supi:do-appu]
повышение скорости (англ. speedup); ~suru повышать скорость; антоним スピードダウン

TN36589"""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "スピードアップ"
    assert result.reading == "すぴーどあっぷ"
    assert result.mainsense == "повышение скорости"


def test_yarxi_double_reading(parser: ArticleParser):
    test_articles = [
        """墨色
[sumiiro], [bokushoku]
цвет (оттенок) туши"""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "墨色"
    assert result.reading == "すみいろ"
    assert result.mainsense == "цвет (оттенок) туши"


def test_bad_article_sashikomu(parser: ArticleParser):
    test_articles = [
        """さしこむ　　
差し込む･差込む
1) (тж. 挿し込む, 插し込む) вкладывать, вставлять;
新聞の中へ広告を差し込む помещать объявление в газете;
2) чувствовать острую (спазматическую) боль;
急に腹が差し込む у меня вдруг появилась острая боль в желудке;
横腹が差し込む колет в боку."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "差し込む･差込む"
    assert result.reading == "さしこむ"
    assert result.mainsense == "вкладывать, вставлять"


def test_article_with_brackets_chimata(parser: ArticleParser):
    test_articles = [
        """ちまた
巷
1) (тж. 街) перекрёсток; улица;
雑沓の街 шумные улицы; перен. городская толчея;
2) развилка дорог; перепутье;
3) грань, граница;
生死の巷をさまよう находиться (блуждать) между жизнью и смертью;
4) арена, сцена чего-л.;
戦火の巷 арена войны; места боёв;
風が少し強く吹けば紅塵万丈の巷となる стоит подуть ветру сильней, как поднимаются тучи пыли;
紅塵の巷から遠い обр. вдалеке от шумной (суетной) толпы."""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "巷"
    assert result.reading == "ちまた"
    assert result.mainsense == "перекрёсток, улица"


def test_really_bad_yarxi_article_mae(parser: ArticleParser):
    test_articles = [
        """前　　　 перед
антоним 後
ZEN  qián
前 [mae] 1) перёд; ~ni впереди; ~no передний; 2) в чьём-л. присутствии, перед кем-л.; 3) ~ni раньше; ~no прежний, прошлый; 4) ~ni заранее; 5) редк., гениталии
お前まえ [o-mae] грубо ты
前々 [maemae] ~kara уже давно, задолго до чего-л.
  В сочетаниях: 
1) передний; впереди; перед чем-л. ("zen", "mae") 
前部 [zenbu] передняя часть, перёд
前輪 [zenrin] редк. [maewa] переднее колесо
前足 [maeashi] передняя нога (лапа); ср. 前脚, 前肢
駅前 [ekimae] привокзальная площадь
目前 [mokuzen] (-no) ~de (~ni) на глазах (перед глазами, под носом) у кого-л.; ср. 目の前 [me-no mae]
2) раньше чего-л. ("zen", "mae") 
以前 [izen] 1) тому назад; до; 2) ~[ni] раньше, прежде; ~no прежний, давнишний; ~kara издавна
午前 [gozen] до полудня, утром
食前 [shokuzen] до еды, перед едой
夜明け前 [yoakemae] перед рассветом
二年前 [ninenmae] два года назад
3) заранее ("zen", "mae") 
前以て [maemotte] заранее, предварительно
前払い [maebarai] предварительная оплата
前金 [maekin] [zenkin] предоплата, аванс
前文 [zenbun] 1) преамбула; 2) предыдущая фраза, вышесказанное
4) предшествующий ("zen") 
前回 [zenkai] прошлый раз; ~no прошлый, предыдущий, последний
前々回 [zenzenkai] позапрошлый (предпоследний) раз; ~no предпоследний
前記 [zenki] ~no вышеупомянутый, вышеуказанный
前条 [zenjo:] предыдущая статья (параграф, пункт)
5) порция; доля ("-mae") 
二人前 [ninin-mae] [futari-mae] ~no на двоих (порция)
6) суффикс после имён придворных дам ("-mae") 
玉藻の前 [tamamo-no-mae] госпожа Тамамо
7) идиоматические сочетания ("-mae") 
名前 [namae] имя
手前 [temae] 1) эта сторона; (-no) ~ni перед чем-л.; 2) скромно я; ~no мой; 3) грубо ты; 4) (-no) ради чего-л.; из уважения к кому-л.; принимая во внимание что-л.; 5) условия жизни, жизнь; 6) см. お手前
男前 [otokomae] красивая наружность (мужчины); ~da быть красивым
腕前 [udemae] умение, способности
気前 [kimae] великодушие, щедрость; см. 気前のいい
建前 [tatemae] 1) [декларируемые, внешние, показные] принципы; иначе 立前антоним 本音 [honne]; 2) [торжественная] закладка нового здания
当たり前 [atarimae] 1) ~[da] естественно, ничего удивительного, само собой разумеется; ~no естественный, неудивительный; правильный; заслуженный; 2) ~no обычный, обыкновенный, нормальный; ~ni как обычно, как всегда

Ключ: 刀 (刂,⺈) (18), 八 (ハ) (12). Штрихов: 9. Исп.: Гакусю (2)
Частотность: 27, JLPT: 4
Nelson: 595; New Nelson: 490; S&H: 2o7.3; Halpern: 2266; Gakken: 38; Heisig: 290; Henshall: 159
KN1614

"""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "前"
    assert result.reading == "まえ"
    assert result.mainsense == "перед"


def test_really_bad_yarxi_article_kon(parser: ArticleParser):
    test_articles = [
        """今　　　 сейчас
KON, KIN (редк.)   jīn
今 [ima] сейчас, теперь; ~no нынешний, теперешний; ~ni скоро; рано или поздно; всё еще; ~ni mo вот-вот, в любой момент; ~kara отныне, впредь; ~made до сих пор; ~de mo и сейчас
今や [imaya] теперь
今めかしい [imamekashii] модный
今めく [imameku] гнаться за модой
今し [imashi] редк.; только что
  В сочетаниях: 
1) теперь; нынешний ("kon", "ima", реже "kin") 
今回 [konkai] в этот раз, на этот раз
今週 [konshu:] эта неделя; на этой неделе
△ 今日 [kyo:] редк. [konnichi] сегодня; ~no сегодняшний; ср. 今日は
今度 [kondo] 1) на (в) этот раз; ~no этот, нынешний; 2) в следующий раз; в другой раз; вскоре; ~no ближайший, предстоящий; 3) недавно; ~no недавний
今直ぐ [imasugu] сейчас [же]
只今 [tadaima] 1) теперь, сейчас; 2) только что; 3) сейчас, скоро; 4) "Вот и я! " (приветствие по возвращении домой) иначе 唯今
今上(陛下) [kinjo:(heika)] кн. ныне царствующий император
2) ещё [один], лишний ("ima-") 
今一つ [imahitotsu] ~[no] ещё один, другой
今一年 [ima-ichinen] ещё один год, лишний год

Ключ: 人 (亻,𠆢) (9). Штрихов: 4. Исп.: Гакусю (2)
Частотность: 49, JLPT: 4
Nelson: 352; New Nelson: 112; S&H: 2a2.10; Halpern: 1968; Gakken: 146; Heisig: 1587; Henshall: 125
KN0943

"""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "今"
    assert result.reading == "いま"
    assert result.mainsense == "сейчас"


def test_bad_article_tokoro(parser: ArticleParser):
    test_articles = [
        """所
[tokoro]
1) место; реже 処; 
2) служебное слово с различными значениями: "когда" и т.п.

TN48965"""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "所"
    assert result.reading == "ところ"
    assert result.mainsense == "место"


def test_bad_article_yakata(parser: ArticleParser):
    test_articles = [
        """館
[yakata]
уст. дворец, палаты; иначе 屋形

TN69757
"""
    ]

    result = parser.process_results(test_articles)[0]

    assert result.word == "館"
    assert result.reading == "やかた"
    assert result.mainsense == "дворец, палаты"
