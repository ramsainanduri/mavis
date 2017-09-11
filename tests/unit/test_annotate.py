import unittest
from mavis.annotate.protein import Domain, DomainRegion, calculate_ORF
from mavis.annotate.base import ReferenceName
import os
import timeout_decorator

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestDomainAlignSeq(unittest.TestCase):

    def test_large_combinations_finishes_with_error(self):
        input_seq = (
            'MADDEDYEEVVEYYTEEVVYEEVPGETITKIYETTTTRTSDYEQSETSKPALAQPALAQPASAKPVERRKVIRKKVDPSK'
            'FMTPYIAHSQKMQDLFSPNKYKEKFEKTKGQPYASTTDTPELRRIKKVQDQLSEVKYRMDGDVAKTICHVDEKAKDIEHA'
            'KKVSQQVSKVLYKQNWEDTKDKYLLPPDAPELVQAVKNTAMFSKKLYTEDWEADKSLFYPYNDSPELRRVAQAQKALSDV'
            'AYKKGLAEQQAQFTPLADPPDIEFAKKVTNQVSKQKYKEDYENKIKGKWSETPCFEVANARMNADNISTRKYQEDFENMK'
            'DQIYFMQTETPEYKMNKKAGVAASKVKYKEDYEKNKGKADYNVLPASENPQLRQLKAAGDALSDKLYKENYEKTKAKSIN'
            'YCETPKFKLDTVLQNFSSDKKYKDSYLKDILGHYVGSFEDPYHSHCMKVTAQNSDKNYKAEYEEDRGKGFFPQTITQEYE'
            'AIKKLDQCKDHTYKVHPDKTKFTQVTDSPVLLQAQVNSKQLSDLNYKAKHESEKFKCHIPPDTPAFIQHKVNAYNLSDNL'
            'YKQDWEKSKAKKFDIKVDAIPLLAAKANTKNTSDVMYKKDYEKNKGKMIGVLSINDDPKMLHSLKVAKNQSDRLYKENYE'
            'KTKAKSMNYCETPKYQLDTQLKNFSEARYKDLYVKDVLGHYVGSMEDPYHTHCMKVAAQNSDKSYKAEYEEDKGKCYFPQ'
            'TITQEYEAIKKLDQCKDHTYKVHPDKTKFTAVTDSPVLLQAQLNTKQLSDLNYKAKHEGEKFKCHIPADAPQFIQHRVNA'
            'YNLSDNVYKQDWEKSKAKKFDIKVDAIPLLAAKANTKNTSDVMYKKDYEKSKGKMIGALSINDDPKMLHSLKTAKNQSDR'
            'EYRKDYEKSKTIYTAPLDMLQVTQAKKSQAIASDVDYKHILHSYSYPPDSINVDLAKKAYALQSDVEYKADYNSWMKGCG'
            'WVPFGSLEMEKAKRASDILNEKKYRQHPDTLKFTSIEDAPITVQSKINQAQRSDIAYKAKGEEIIHKYNLPPDLPQFIQA'
            'KVNAYNISENMYKADLKDLSKKGYDLRTDAIPIRAAKAARQAASDVQYKKDYEKAKGKMVGFQSLQDDPKLVHYMNVAKI'
            'QSDREYKKDYEKTKSKYNTPHDMFNVVAAKKAQDVVSNVNYKHSLHHYTYLPDAMDLELSKNMMQIQSDNVYKEDYNNWM'
            'KGIGWIPIGSLDVEKVKKAGDALNEKKYRQHPDTLKFTSIVDSPVMVQAKQNTKQVSDILYKAKGEDVKHKYTMSPDLPQ'
            'FLQAKCNAYNISDVCYKRDWYDLIAKGNNVLGDAIPITAAKASRNIASDYKYKEAYEKSKGKHVGFRSLQDDPKLVHYMN'
            'VAKLQSDREYKKNYENTKTSYHTPGDMVSITAAKMAQDVATNVNYKQPLHHYTYLPDAMSLEHTRNVNQIQSDNVYKDEY'
            'NSFLKGIGWIPIGSLEVEKVKKAGDALNERKYRQHPDTVKFTSVPDSMGMVLAQHNTKQLSDLNYKVEGEKLKHKYTIDP'
            'ELPQFIQAKVNALNMSDAHYKADWKKTIAKGYDLRPDAIPIVAAKSSRNIASDCKYKEAYEKAKGKQVGFLSLQDDPKLV'
            'HYMNVAKIQSDREYKKGYEASKTKYHTPLDMVSVTAAKKSQEVATNANYRQSYHHYTLLPDALNVEHSRNAMQIQSDNLY'
            'KSDFTNWMKGIGWVPIESLEVEKAKKAGEILSEKKYRQHPEKLKFTYAMDTMEQALNKSNKLNMDKRLYTEKWNKDKTTI'
            'HVMPDTPDILLSRVNQITMSDKLYKAGWEEEKKKGYDLRPDAIAIKAARASRDIASDYKYKKAYEQAKGKHIGFRSLEDD'
            'PKLVHFMQVAKMQSDREYKKGYEKSKTSFHTPVDMLSVVAAKKSQEVATNANYRNVIHTYNMLPDAMSFELAKNMMQIQS'
            'DNQYKADYADFMKGIGWLPLGSLEAEKNKKAMEIISEKKYRQHPDTLKYSTLMDSMNMVLAQNNAKIMNEHLYKQAWEAD'
            'KTKVHIMPDIPQIILAKANAINMSDKLYKLSLEESKKKGYDLRPDAIPIKAAKASRDIASDYKYKYNYEKGKGKMVGFRS'
            'LEDDPKLVHSMQVAKMQSDREYKKNYENTKTSYHTPADMLSVTAAKDAQANITNTNYKHLIHKYILLPDAMNIELTRNMN'
            'RIQSDNEYKQDYNEWYKGLGWSPAGSLEVEKAKKATEYASDQKYRQHPSNFQFKKLTDSMDMVLAKQNAHTMNKHLYTID'
            'WNKDKTKIHVMPDTPDILQAKQNQTLYSQKLYKLGWEEALKKGYDLPVDAISVQLAKASRDIASDYKYKQGYRKQLGHHV'
            'GFRSLQDDPKLVLSMNVAKMQSEREYKKDFEKWKTKFSSPVDMLGVVLAKKCQELVSDVDYKNYLHQWTCLPDQNDVVQA'
            'KKVYELQSENLYKSDLEWLRGIGWSPLGSLEAEKNKRASEIISEKKYRQPPDRNKFTSIPDAMDIVLAKTNAKNRSDRLY'
            'REAWDKDKTQIHIMPDTPDIVLAKANLINTSDKLYRMGYEELKRKGYDLPVDAIPIKAAKASREIASEYKYKEGFRKQLG'
            'HHIGARNIEDDPKMMWSMHVAKIQSDREYKKDFEKWKTKFSSPVDMLGVVLAKKCQTLVSDVDYKNYLHQWTCLPDQSDV'
            'IHARQAYDLQSDNLYKSDLQWLKGIGWMTSGSLEDEKNKRATQILSDHVYRQHPDQFKFSSLMDSIPMVLAKNNAITMNH'
            'RLYTEAWDKDKTTVHIMPDTPEVLLAKQNKVNYSEKLYKLGLEEAKRKGYDMRVDAIPIKAAKASRDIASEFKYKEGYRK'
            'QLGHHIGARAIRDDPKMMWSMHVAKIQSDREYKKDFEKWKTKFSSPVDMLGVVLAKKCQTLVSDVDYKNYLHQWTCLPDQ'
            'SDVIHARQAYDLQSDNMYKSDLQWMRGIGWVSIGSLDVEKCKRATEILSDKIYRQPPDRFKFTSVTDSLEQVLAKNNAIT'
            'MNKRLYTEAWDKDKTQIHIMPDTPEIMLARMNKINYSESLYKLANEEAKKKGYDLRSDAIPIVAAKASRDIISDYKYKDG'
            'YCKQLGHHIGARNIEDDPKMMWSMHVAKIQSDREYKKDFEKWKTKFSSPVDMLGVVLAKKCQTLVSDVDYKNYLHEWTCL'
            'PDQSDVIHARQAYDLQSDNIYKSDLQWLRGIGWVPIGSMDVVKCKRATEILSDNIYRQPPDKLKFTSVTDSLEQVLAKNN'
            'ALNMNKRLYTEAWDKDKTQIHIMPDTPEIMLARQNKINYSETLYKLANEEAKKKGYDLRSDAIPIVAAKASRDVISDYKY'
            'KDGYRKQLGHHIGARNIEDDPKMMWSMHVAKIQSDREYKKDFEKWKTKFSSPVDMLGVVLAKKCQTLVSDVDYKNYLHEW'
            'TCLPDQNDVIHARQAYDLQSDNIYKSDLQWLRGIGWVPIGSMDVVKCKRAAEILSDNIYRQPPDKLKFTSVTDSLEQVLA'
            'KNNALNMNKRLYTEAWDKDKTQVHIMPDTPEIMLARQNKINYSESLYRQAMEEAKKEGYDLRSDAIPIVAAKASRDIASD'
            'YKYKEAYRKQLGHHIGARAVHDDPKIMWSLHIAKVQSDREYKKDFEKYKTRYSSPVDMLGIVLAKKCQTLVSDVDYKHPL'
            'HEWICLPDQNDIIHARKAYDLQSDNLYKSDLEWMKGIGWVPIDSLEVVRAKRAGELLSDTIYRQRPETLKFTSITDTPEQ'
            'VLAKNNALNMNKRLYTEAWDNDKKTIHVMPDTPEIMLAKLNRINYSDKLYKLALEESKKEGYDLRLDAIPIQAAKASRDI'
            'ASDYKYKEGYRKQLGHHIGARNIKDDPKMMWSIHVAKIQSDREYKKEFEKWKTKFSSPVDMLGVVLAKKCQILVSDIDYK'
            'HPLHEWTCLPDQNDVIQARKAYDLQSDAIYKSDLEWLRGIGWVPIGSVEVEKVKRAGEILSDRKYRQPADQLKFTCITDT'
            'PEIVLAKNNALTMSKHLYTEAWDADKTSIHVMPDTPDILLAKSNSANISQKLYTKGWDESKMKDYDLRADAISIKSAKAS'
            'RDIASDYKYKEAYEKQKGHHIGAQSIEDDPKIMCAIHAGKIQSEREYKKEFQKWKTKFSSPVDMLSILLAKKCQTLVTDI'
            'DYRNYLHEWTCMPDQNDIIQAKKAYDLQSDSVYKADLEWLRGIGWMPEGSVEMNRVKVAQDLVNERLYRTRPEALSFTSI'
            'VDTPEVVLAKANSLQISEKLYQEAWNKDKSNITIPSDTPEMLQAHINALQISNKLYQKDWNDAKQKGYDIRADAIEIKHA'
            'KASREIASEYKYKEGYRKQLGHHMGFRTLQDDPKSVWAIHAAKIQSDREYKKAYEKSKGIHNTPLDMMSIVQAKKCQVLV'
            'SDIDYRNYLHQWTCLPDQNDVIQAKKAYDLQSDNLYKSDLEWLKGIGWLPEGSVEVMRVKNAQNLLNERLYRIKPEALKF'
            'TSIVDTPEVIQAKINAVQISEPLYRDAWEKEKANVNVPADTPLMLQSKINALQISNKRYQQAWEDVKMTGYDLRADAIGI'
            'QHAKASRDIASDYLYKTAYEKQKGHYIGCRSAKEDPKLVWAANVLKMQNDRLYKKAYNDHKAKISIPVDMVSISAAKEGQ'
            'ALASDVDYRHYLHHWSCFPDQNDVIQARKAYDLQSDSVYKADLEWLRGIGWMPEGSVEMNRVKVAQDLVNERLYRTRPEA'
            'LSFTSIVDTPEVVLAKANSLQISEKLYQEAWNKDKSNITIPSDTPEMLQAHINALQISNKLYQKDWNDTKQKGYDIRADA'
            'IEIKHAKASREIASEYKYKEGYRKQLGHHMGFRTLQDDPKSVWAIHAAKIQSDREYKKAYEKSKGIHNTPLDMMSIVQAK'
            'KCQVLVSDIDYRNYLHQWTCLPDQNDVIQAKKAYDLQSDNLYKSDLEWLKGIGWLPEGSVEVMRVKNAQNLLNERLYRIK'
            'PEALKFTSIVDTPEVIQAKINAVQISEPLYRNAWEKEKANVNVPADTPLMLQSKINALQISNKRYQQAWEDVKMTGYDLR'
            'ADAIGIQHAKASRDIASDYLYKTAYEKQKGHYIGCRSAKEDPKLVWAANVLKMQNDRLYKKAYNDHKAKISIPVDMVSIS'
            'AAKEGQALASDVDYRHYLHHWSCFPDQNDVIQARKAYDLQSDSVYKADLEWLRGIGWMPEGSVEMNRVKVAQDLVNERLY'
            'RTRPEALSFTSIVDTPEVVLAKANSLQISEKLYQEAWNKDKSNITIPSDTPEMLQAHINALQISNKLYQKDWNDTKQKGY'
            'DIRADAIEIKHAKASREIASEYKYKEGYRKQLGHHMGFRTLQDDPKSVWAIHAAKIQSDREYKKAYEKSKGIHNTPLDMM'
            'SIVQAKKCQVLVSDIDYRNYLHQWTCLPDQNDVIQAKKAYDLQSDNLYKSDLEWLKGIGWLPEGSVEVMRVKNAQNLLNE'
            'RLYRIKPEALKFTSIVDTPEVIQAKINAVQISEPLYRDAWEKEKANVNVPADTPLMLQSKINALQISNKRYQQAWEDVKM'
            'TGYDLRADAIGIQHAKASRDIASDYLYKTAYEKQKGHYIGCRSAKEDPKLVWAANVLKMQNDRLYKKAYNDHKAKISIPV'
            'DMVSISAAKEGQALASDVDYRHYLHRWSCFPDQNDVIQARKAYDLQSDALYKADLEWLRGIGWMPQGSPEVLRVKNAQNI'
            'FCDSVYRTPVVNLKYTSIVDTPEVVLAKSNAENISIPKYREVWDKDKTSIHIMPDTPEINLARANALNVSNKLYREGWDE'
            'MKAGCDVRLDAIPIQAAKASREIASDYKYKLDHEKQKGHYVGTLTARDDNKIRWALIADKLQNEREYRLDWAKWKAKIQS'
            'PVDMLSILHSKNSQALVSDMDYRNYLHQWTCMPDQNDVIQAKKAYELQSDNVYKADLEWLRGIGWMPNDSVSVNHAKHAA'
            'DIFSEKKYRTKIETLNFTPVDDRVDYVTAKQSGEILDDIKYRKDWNATKSKYTLTETPLLHTAQEAARILDQYLYKEGWE'
            'RQKATGYILPPDAVPFVHAHHCNDVQSELKYKAEHVKQKGHYVGVPTMRDDPKLVWFEHAGQIQNERLYKEDYHKTKAKI'
            'NIPADMVSVLAAKQGQTLVSDIDYRNYLHQWMCHPDQNDVIQARKAYDLQSDNVYRADLEWLRGIGWIPLDSVDHVRVTK'
            'NQEMMSQIKYKKNALENYPNFRSVVDPPEIVLAKINSVNQSDVKYKETFNKAKGKYTFSPDTPHISHSKDMGKLYSTILY'
            'KGAWEGTKAYGYTLDERYIPIVGAKHADLVNSELKYKETYEKQKGHYLAGKVIGEFPGVVHCLDFQKMRSALNYRKHYED'
            'TKANVHIPNDMMNHVLAKRCQYILSDLEYRHYFHQWTSLLEEPNVIRVRNAQEILSDNVYKDDLNWLKGIGCYVWDTPQI'
            'LHAKKSYDLQSQLQYTAAGKENLQNYNLVTDTPLYVTAVQSGINASEVKYKENYHQIKDKYTTVLETVDYDRTRNLKNLY'
            'SSNLYKEAWDRVKATSYILPSSTLSLTHAKNQKHLASHIKYREEYEKFKALYTLPRSVDDDPNTARCLRVGKLNIDRLYR'
            'SVYEKNKMKIHIVPDMVEMVTAKDSQKKVSEIDYRLRLHEWICHPDLQVNDHVRKVTDQISDIVYKDDLNWLKGIGCYVW'
            'DTPEILHAKHAYDLRDDIKYKAHMLKTRNDYKLVTDTPVYVQAVKSGKQLSDAVYHYDYVHSVRGKVAPTTKTVDLDRAL'
            'HAYKLQSSNLYKTSLRTLPTGYRLPGDTPHFKHIKDTRYMSSYFKYKEAYEHTKAYGYTLGPKDVPFVHVRRVNNVTSER'
            'LYRELYHKLKDKIHTTPDTPEIRQVKKTQEAVSELIYKSDFFKMQGHMISLPYTPQVIHCRYVGDITSDIKYKEDLQVLK'
            'GFGCFLYDTPDMVRSRHLRKLWSNYLYTDKARKMRDKYKVVLDTPEYRKVQELKTHLSELVYRAAGKKQKSIFTSVPDTP'
            'DLLRAKRGQKLQSQYLYVELATKERPHHHAGNQTTALKHAKDVKDMVSEKKYKIQYEKMKDKYTPVPDTPILIRAKRAYW'
            'NASDLRYKETFQKTKGKYHTVKDALDIVYHRKVTDDISKIKYKENYMSQLGIWRSIPDRPEHFHHRAVTDTVSDVKYKED'
            'LTWLKGIGCYAYDTPDFTLAEKNKTLYSKYKYKEVFERTKSDFKYVADSPINRHFKYATQLMNERKYKSSAKMFLQHGCN'
            'EILRPDMLTALYNSHMWSQIKYRKNYEKSKDKFTSIVDTPEHLRTTKVNKQISDILYKLEYNKAKPRGYTTIHDTPMLLH'
            'VRKVKDEVSDLKYKEVYQRNKSNCTIEPDAVHIKAAKDAYKVNTNLDYKKQYEANKAHWKWTPDRPDFLQAAKSSLQQSD'
            'FEYKLDREFLKGCKLSVTDDKNTVLALRNTLIESDLKYKEKHVKERGTCHAVPDTPQILLAKTVSNLVSENKYKDHVKKH'
            'LAQGSYTTLPETRDTVHVKEVTKHVSDTNYKKKFVKEKGKSNYSIMLEPPEVKHAMEVAKKQSDVAYRKDAKENLHYTTV'
            'ADRPDIKKATQAAKQASEVEYRAKHRKEGSHGLSMLGRPDIEMAKKAAKLSSQVKYRENFDKEKGKTPKYNPKDSQLYKV'
            'MKDANNLASEVKYKADLKKLHKPVTDMKESLIMNHVLNTSQLASSYQYKKKYEKSKGHYHTIPDNLEQLHLKEATELQSI'
            'VKYKEKYEKERGKPMLDFETPTYITAKESQQMQSGKEYRKDYEESIKGRNLTGLEVTPALLHVKYATKIASEKEYRKDLE'
            'ESIRGKGLTEMEDTPDMLRAKNATQILNEKEYKRDLELEVKGRGLNAMANETPDFMRARNATDIASQIKYKQSAEMEKAN'
            'FTSVVDTPEIIHAQQVKNLSSQKKYKEDAEKSMSYYETVLDTPEIQRVRENQKNFSLLQYQCDLKNSKGKITVVQDTPEI'
            'LRVKENQKNFSSVLYKEDVSPGTAIGKTPEMMRVKQTQDHISSVKYKEAIGQGTPIPDLPEVKRVKETQKHISSVMYKEN'
            'LGTGIPTTVTPEIERVKRNQENFSSVLYKENLGKGIPTPITPEMERVKRNQENFSSILYKENLSKGTPLPVTPEMERVKL'
            'NQENFSSVLYKENVGKGIPIPITPEMERVKHNQENFSSVLYKENLGTGIPIPITPEMQRVKHNQENLSSVLYKENMGKGT'
            'PLPVTPEMERVKHNQENISSVLYKENMGKGTPLPVTPEMERVKHNQENISSVLYKENMGKGTPLAVTPEMERVKHNQENI'
            'SSVLYKENVGKATATPVTPEMQRVKRNQENISSVLYKENLGKATPTPFTPEMERVKRNQENFSSVLYKENMRKATPTPVT'
            'PEMERAKRNQENISSVLYSDSFRKQIQGKAAYVLDTPEMRRVRETQRHISTVKYHEDFEKHKGCFTPVVTDPITERVKKN'
            'MQDFSDINYRGIQRKVVEMEQKRNDQDQETITGLRVWRTNPGSVFDYDPAEDNIQSRSLHMINVQAQRRSREQSRSASAL'
            'SISGGEEKSEHSEAPDHHLSTYSDGGVFAVSTAYKHAKTTELPQQRSSSVATQQTTVSSIPSHPSTAGKIFRAMYDYMAA'
            'DADEVSFKDGDAIINVQAIDEGWMYGTVQRTGRTGMLPANYVEAI*'
        )

        region_seqs = [
            'TPYIAHSQKMQDLFSPNKYKEKFEKTKG',
            'DTPELRRIKKVQDQLSEVKYRMDGD',
            'DIEHAKKVSQQVSKVLYKQNWEDTK',
            'DAPELVQAVKNTAMFSKKLYTEDWEADK',
            'DPPDIEFAKKVTNQVSKQKYKEDYEN',
            'ETPEYKMNKKAGVAASKVKYKEDYEKNKG',
            'NPQLRQLKAAGDALSDKLYKENYEKTKA',
            'DSPVLLQAQVNSKQLSDLNYKAKHESEK',
            'DTPAFIQHKVNAYNLSDNLYKQDWEKSKA',
            'DAIPLLAAKANTKNTSDVMYKKDYEKNKG',
            'DDPKMLHSLKVAKNQSDRLYKENYEKTKA',
            'DAPQFIQHRVNAYNLSDNVYKQDWEKSKA',
            'DAIPLLAAKANTKNTSDVMYKKDYEKSKG',
            'DDPKMLHSLKTAKNQSDREYRKDYEKSK',
            'DSINVDLAKKAYALQSDVEYKADYNSW',
            'DAIPIRAAKAARQAASDVQYKKDYEKAKG',
            'DDPKLVHYMNVAKIQSDREYKKDYEKTKS',
            'DAMDLELSKNMMQIQSDNVYKEDYNNWM',
            'DSPVMVQAKQNTKQVSDILYKAKGEDVKH',
            'DLPQFLQAKCNAYNISDVCYKRDWYD',
            'DAIPITAAKASRNIASDYKYKEAYEKSKG',
            'DDPKLVHYMNVAKLQSDREYKKNYENTK',
            'PQFIQAKVNALNMSDAHYKADWKKTI',
            'DAIPIVAAKSSRNIASDCKYKEAYEKAKG',
            'DDPKLVHYMNVAKIQSDREYKKGYEASK',
            'DTPDILLSRVNQITMSDKLYKAGWEEEKK',
            'DAIAIKAARASRDIASDYKYKKAYEQAKG',
            'DDPKLVHFMQVAKMQSDREYKKGYEKSK',
            'DAMSFELAKNMMQIQSDNQYKADYA',
            'DSMNMVLAQNNAKIMNEHLYKQAWEADK',
            'DIPQIILAKANAINMSDKLYKLSLEESKK',
            'DAIPIKAAKASRDIASDYKYKYNYEKGKG',
            'DDPKLVHSMQVAKMQSDREYKKNYENTK',
            'DSMDMVLAKQNAHTMNKHLYTIDWNKDK',
            'DTPDILQAKQNQTLYSQKLYKLGWEEA',
            'DAISVQLAKASRDIASDYKYKQGYRKQLG',
            'DDPKLVLSMNVAKMQSEREYKKDFEKWK',
            'QNDVVQAKKVYELQSENLYKSDLEWLRG',
            'DAMDIVLAKTNAKNRSDRLYREAWDKDK',
            'DTPDIVLAKANLINTSDKLYRMGYEELK',
            'DAIPIKAAKASREIASEYKYKEGFRKQLG',
            'DDPKMMWSMHVAKIQSDREYKKDFEKWK',
            'DVIHARQAYDLQSDNLYKSDLQWLKG',
            'DSIPMVLAKNNAITMNHRLYTEAWDKDK',
            'DTPEVLLAKQNKVNYSEKLYKLGLEEAK',
            'DDPKMMWSMHVAKIQSDREYKKDFEKWK',
            'DSLEQVLAKNNAITMNKRLYTEAWDKDK',
            'DTPEIMLARMNKINYSESLYKLANEEAK',
            'DDPKMMWSMHVAKIQSDREYKKDFEKWK',
            'DSLEQVLAKNNALNMNKRLYTEAWDKDK',
            'DTPEIMLARQNKINYSETLYKLANEEAK',
            'DAIPIVAAKASRDVISDYKYKDGYRKQLG',
            'DDPKMMWSMHVAKIQSDREYKKDFEKWK',
            'DSLEQVLAKNNALNMNKRLYTEAWDKDK',
            'DTPEIMLARQNKINYSESLYRQAMEEAKK',
            'DAIPIVAAKASRDIASDYKYKEAYRKQLG',
            'DDPKIMWSLHIAKVQSDREYKKDFEKYK',
            'QNDIIHARKAYDLQSDNLYKSDLEWMKG',
            'DTPEQVLAKNNALNMNKRLYTEAWDNDKK',
            'DTPEIMLAKLNRINYSDKLYKLALEESKK',
            'DAIPIQAAKASRDIASDYKYKEGYRKQLG',
            'DDPKMMWSIHVAKIQSDREYKKEFEKWK',
            'DTPEIVLAKNNALTMSKHLYTEAWDADK',
            'DTPDILLAKSNSANISQKLYTKGWDESK',
            'DAISIKSAKASRDIASDYKYKEAYEKQKG',
            'DDPKIMCAIHAGKIQSEREYKKEFQKWK',
            'QNDIIQAKKAYDLQSDSVYKADLEWLRG',
            'DTPEVVLAKANSLQISEKLYQEAWNKDKS',
            'DTPEMLQAHINALQISNKLYQKDWNDAK',
            'DAIEIKHAKASREIASEYKYKEGYRKQLG',
            'DDPKSVWAIHAAKIQSDREYKKAYEKSKG',
            'NDVIQAKKAYDLQSDNLYKSDLEWLKG',
            'DTPEVIQAKINAVQISEPLYRDAWEKEKA',
            'DAIGIQHAKASRDIASDYLYKTAYEKQKG',
            'NDVIQARKAYDLQSDSVYKADLEWLRG',
            'DTPEVVLAKANSLQISEKLYQEAWNKDKS',
            'DTPEMLQAHINALQISNKLYQKDWNDTK',
            'DAIEIKHAKASREIASEYKYKEGYRKQLG',
            'DDPKSVWAIHAAKIQSDREYKKAYEKSKG',
            'NDVIQAKKAYDLQSDNLYKSDLEWLKG',
            'DTPEVIQAKINAVQISEPLYRNAWEKEKA',
            'DAIGIQHAKASRDIASDYLYKTAYEKQKG',
            'NDVIQARKAYDLQSDSVYKADLEWLRG',
            'DTPEVVLAKANSLQISEKLYQEAWNKDKS',
            'DTPEMLQAHINALQISNKLYQKDWNDTK',
            'DAIEIKHAKASREIASEYKYKEGYRKQLG',
            'DDPKSVWAIHAAKIQSDREYKKAYEKSKG',
            'NDVIQAKKAYDLQSDNLYKSDLEWLKG',
            'DTPEVIQAKINAVQISEPLYRDAWEKEKA',
            'DAIGIQHAKASRDIASDYLYKTAYEKQKG',
            'NDVIQARKAYDLQSDALYKADLEWLRG',
            'DTPEVVLAKSNAENISIPKYREVWDKDK',
            'DTPEINLARANALNVSNKLYREGWDEMKA',
            'DAIPIQAAKASREIASDYKYKLDHEKQKG',
            'NDVIQAKKAYELQSDNVYKADLEWLRG',
            'DRVDYVTAKQSGEILDDIKYRKDWNATKS',
            'DAVPFVHAHHCNDVQSELKYKAEHVKQKG',
            'DDPKLVWFEHAGQIQNERLYKEDYHKTKA',
            'NDVIQARKAYDLQSDNVYRADLEWLRG',
            'DPPEIVLAKINSVNQSDVKYKETFNKAKG',
            'DTPHISHSKDMGKLYSTILYKGAWEGTKA',
            'PIVGAKHADLVNSELKYKETYEKQKG',
            'PNVIRVRNAQEILSDNVYKDDLNWLKG',
            'DTPQILHAKKSYDLQSQLQYTAAGKEN',
            'DTPLYVTAVQSGINASEVKYKENYHQIK',
            'LSLTHAKNQKHLASHIKYREEYEKFKA',
            'DTPEILHAKHAYDLRDDIKYKAH',
            'DTPHFKHIKDTRYMSSYFKYKEAYEHTKA',
            'DTPEIRQVKKTQEAVSELIYKSDFFKMQG',
            'TPQVIHCRYVGDITSDIKYKEDLQVLK',
            'DTPDMVRSRHLRKLWSNYLYTDKARKMR',
            'DTPILIRAKRAYWNASDLRYKETFQKTKG',
            'DRPEHFHHRAVTDTVSDVKYKEDLTWLKG',
            'DTPDFTLAEKNKTLYSKYKYKEVFERTKS',
            'RPDMLTALYNSHMWSQIKYRKNYEKSK',
            'DTPEHLRTTKVNKQISDILYKLEYNKAK',
            'DTPMLLHVRKVKDEVSDLKYKEVYQRNK',
            'DTPQILLAKTVSNLVSENKYKDHVKK',
            'ETRDTVHVKEVTKHVSDTNYKKKFVKEKG',
            'RPDIEMAKKAAKLSSQVKYRENFDKEKG',
            'DNLEQLHLKEATELQSIVKYKEKYEKERG',
            'ETPTYITAKESQQMQSGKEYRKDYEESI',
            'TPALLHVKYATKIASEKEYRKDLEES',
            'DTPDMLRAKNATQILNEKEYKRDLE',
            'ETPDFMRARNATDIASQIKYKQSAEMEKA',
            'DTPEIIHAQQVKNLSSQKKYKEDAEKSM',
            'DTPEIQRVRENQKNFSLLQYQCDLKNSKG',
            'DTPEILRVKENQKNFSSVLYKED',
            'TPEMMRVKQTQDHISSVKYKEA',
            'TPEIERVKRNQENFSSVLYKENLGK',
            'TPEMERVKRNQENFSSILYKENL',
            'TPEMERVKLNQENFSSVLYKEN',
            'TPEMERVKHNQENFSSVLYKEN',
            'TPEMQRVKHNQENLSSVLYKENM',
            'TPEMERVKHNQENISSVLYKENM',
            'TPEMERVKHNQENISSVLYKENM',
            'TPEMERVKHNQENISSVLYKENVGK',
            'TPEMQRVKRNQENISSVLYKENLGKA',
            'TPEMERVKRNQENFSSVLYKENMRKA',
            'TPEMERAKRNQENISSVLYSDSFRKQI',
            'DTPEMRRVRETQRHISTVKYHEDFEKHKG'
        ]
        regions = []
        p = 1
        for seq in region_seqs:
            regions.append(DomainRegion(p, p + len(seq) - 1, seq=seq))
            p += len(seq)
        d = Domain('name', regions=regions)
        with self.assertRaises(UserWarning):
            d.align_seq(input_seq)


class TestCalculateORF(unittest.TestCase):
    def setUp(self):
        # load the sequence
        with open(os.path.join(DATA_DIR, 'calc_orf_test_sequence.fa'), 'r') as fh:
            self.seq = fh.readlines()[0].strip()

    @timeout_decorator.timeout(20)
    def test_very_long(self):
        calculate_ORF(self.seq, 300)


class TestReferenceName(unittest.TestCase):
    def test_naked_vs_naked_str(self):
        self.assertEqual('1', ReferenceName('1'))
        self.assertNotEqual('2', ReferenceName('1'))
        self.assertTrue(ReferenceName('1') == '1')
        self.assertTrue(ReferenceName('1') != '2')

    def test_naked_vs_prefixed_str(self):
        self.assertEqual('chr1', ReferenceName('1'))
        self.assertNotEqual('chr2', ReferenceName('1'))
        self.assertTrue(ReferenceName('1') == 'chr1')
        self.assertTrue(ReferenceName('1') != 'chr2')

    def test_prefixed_vs_prefixed_str(self):
        self.assertEqual('chr1', ReferenceName('chr1'))
        self.assertNotEqual('chr2', ReferenceName('chr1'))
        self.assertTrue(ReferenceName('chr1') == 'chr1')
        self.assertTrue(ReferenceName('chr1') != 'chr2')

    def test_prefixed_vs_naked_str(self):
        self.assertEqual('1', ReferenceName('chr1'))
        self.assertNotEqual('2', ReferenceName('chr1'))
        self.assertTrue(ReferenceName('chr1') == '1')

    def test_obj_comparison(self):
        r = ReferenceName('1')
        rprefix = ReferenceName('chr1')
        r2 = ReferenceName('2')
        r2prefix = ReferenceName('chr2')
        self.assertEqual(r, rprefix)
        self.assertEqual(rprefix, r)
        self.assertEqual(rprefix, ReferenceName('chr1'))
        self.assertEqual(r, ReferenceName('1'))
        self.assertNotEqual(r2, rprefix)
        self.assertNotEqual(r2prefix, rprefix)
        self.assertNotEqual(r2, r)
        self.assertNotEqual(r2prefix, r)
        self.assertTrue(r == rprefix)
        self.assertTrue(r != r2prefix)
        self.assertFalse(r != rprefix)
