/**
 *
 * RenderPipeline
 *
 * Copyright (c) 2014-2016 tobspr <tobias.springer1@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 */

#pragma once

/*

2D Poisson Disks

*/
CONST_ARRAY vec2 poisson_disk_2D_12[12] = vec2[](
    vec2(-0.40308118105, -0.608544825061),
    vec2(0.587495047536, 0.809142190553),
    vec2(-0.735324325824, 0.674768773024),
    vec2(0.886160134258, -0.45735467724),
    vec2(-0.000740642465604, 0.166906952881),
    vec2(-0.991008190801, -0.091222644662),
    vec2(0.30035192628, -0.951228960887),
    vec2(-0.0996379258058, 0.993861547317),
    vec2(0.970569981, 0.239765820945),
    vec2(0.297296872379, -0.355085398853),
    vec2(-0.528962916575, 0.170871425911),
    vec2(0.478344417303, 0.307371591164)
);



CONST_ARRAY vec2 poisson_disk_2D_16[16] = vec2[](
    vec2(0.577144936745, 0.290107406714),
    vec2(-0.900473190035, -0.42857366637),
    vec2(0.257257614194, -0.955728042151),
    vec2(-0.581504478389, 0.805658460374),
    vec2(-0.101361123132, -0.192307160696),
    vec2(0.894027012504, -0.436667554896),
    vec2(0.181300778811, 0.960573846805),
    vec2(-0.958680507794, 0.24760556048),
    vec2(-0.424334528348, -0.899654593117),
    vec2(-0.105095493157, 0.42081868091),
    vec2(0.367563080624, -0.431966796474),
    vec2(-0.48834323933, 0.102277807315),
    vec2(0.621807382228, 0.769540067834),
    vec2(0.981849335379, 0.0426728212516),
    vec2(-0.0626045144966, -0.643378425815),
    vec2(-0.464589674286, -0.451470757519)
);

CONST_ARRAY vec2 poisson_disk_2D_32[32] = vec2[](
    vec2(-0.975722323102, -0.204041500502),
    vec2(-0.17982006467, -0.0658298867836),
    vec2(-0.584240116577, -0.236750145783),
    vec2(-0.696158968955, -0.679269066752),
    vec2(-0.302953619815, -0.508182541804),
    vec2(-0.239771849583, -0.970392115487),
    vec2(-0.0117289780809, -0.78878924143),
    vec2(0.0338629451354, -0.264913968097),
    vec2(0.130627664399, -0.538613496243),
    vec2(0.249697773202, -0.961353458812),
    vec2(0.649377129975, -0.760086265064),
    vec2(0.461349548925, -0.487640734711),
    vec2(0.901989105018, -0.425872974546),
    vec2(0.588380414145, -0.164567935266),
    vec2(0.21427563112, -0.0342795470405),
    vec2(0.982079820339, -0.0592545716552),
    vec2(0.613992626698, 0.188864086279),
    vec2(0.952038718849, 0.305862220705),
    vec2(0.69809494032, 0.494314903982),
    vec2(0.307582379822, 0.359650539525),
    vec2(0.601372258861, 0.795503757978),
    vec2(0.110660318447, 0.646072406616),
    vec2(0.0928629901783, 0.986177780289),
    vec2(-0.0141053563478, 0.238475699429),
    vec2(-0.144324225302, 0.803231336381),
    vec2(-0.221868664183, 0.518204128708),
    vec2(-0.420534437057, 0.907150252965),
    vec2(-0.53048141882, 0.442324212812),
    vec2(-0.770868549304, 0.631188922305),
    vec2(-0.324885182115, 0.208722763881),
    vec2(-0.640874805455, 0.15694001488),
    vec2(-0.986033536158, 0.143593464357)
);


CONST_ARRAY vec2 poisson_disk_2D_64[64] = vec2[](
    vec2(-0.02862636095, 0.394651943881),
    vec2(0.0479226730762, -0.998498252185),
    vec2(0.967033029711, -0.250764721595),
    vec2(-0.938740126397, -0.340834413221),
    vec2(0.805015666316, 0.56897293049),
    vec2(-0.870584636996, 0.48947099945),
    vec2(0.234725046616, -0.289911320208),
    vec2(0.291656434668, 0.956370391675),
    vec2(-0.398191149781, 0.910646710828),
    vec2(-0.549763782523, -0.829966608897),
    vec2(-0.360281095044, -0.127242140926),
    vec2(0.623391159907, -0.779061245191),
    vec2(0.449909199614, 0.184655461646),
    vec2(-0.158014162468, -0.559241244918),
    vec2(-0.464053499223, 0.315963132387),
    vec2(0.97957431522, 0.178415774787),
    vec2(-0.816825372813, 0.0684375481126),
    vec2(0.403221790812, 0.578240642498),
    vec2(0.610192846895, -0.392825335662),
    vec2(-0.00194765710599, 0.0117389567625),
    vec2(0.240762513914, -0.672112297885),
    vec2(-0.0407705200963, 0.777188129976),
    vec2(-0.57624627145, -0.454660994111),
    vec2(0.685513457591, -0.0661109631938),
    vec2(-0.564946424059, 0.622438154693),
    vec2(-0.25823397985, -0.929255281851),
    vec2(-0.271076514027, 0.571388100846),
    vec2(-0.0632092229563, -0.277591046896),
    vec2(0.606681593183, 0.792295327642),
    vec2(-0.665360224235, -0.180336251622),
    vec2(0.37345091166, -0.925379222212),
    vec2(0.714356325531, 0.287894286057),
    vec2(-0.249651150721, 0.139101453711),
    vec2(0.857202328079, -0.512119313764),
    vec2(0.269389775139, -0.0203446642834),
    vec2(0.237956569514, 0.360944780895),
    vec2(-0.78838984385, -0.611062202248),
    vec2(-0.554793585973, 0.0610659886912),
    vec2(0.145787844263, 0.599804041778),
    vec2(-0.337743819191, -0.377870172153),
    vec2(0.460800555795, -0.181068340564),
    vec2(0.000242881641263, -0.752476961611),
    vec2(0.0779158925609, -0.482103053681),
    vec2(-0.711164632612, 0.299174087861),
    vec2(-0.394131120768, -0.62565136215),
    vec2(-0.960099091522, 0.264615019953),
    vec2(-0.986187810884, -0.103184832294),
    vec2(-0.157372839418, 0.984980893974),
    vec2(0.465303773905, -0.588616363222),
    vec2(0.0702598904154, 0.972713038657),
    vec2(0.903639588251, -0.0285313272419),
    vec2(0.518663526189, 0.396044767737),
    vec2(-0.24404867707, 0.355853242),
    vec2(0.919736960445, 0.385782212552),
    vec2(0.149231779564, 0.164557284011),
    vec2(0.406226946967, 0.790171200908),
    vec2(0.757353139981, -0.254043865252),
    vec2(0.408805186322, -0.393705951484),
    vec2(-0.25205797587, 0.767290375367),
    vec2(-0.061392903936, 0.200788045499),
    vec2(0.604134564527, 0.57539601135),
    vec2(0.169066957873, 0.800392409069),
    vec2(-0.164741503624, -0.0982259589837),
    vec2(0.675622058068, -0.588454027961)
);



/*


3D Poisson Disks


*/

CONST_ARRAY vec3 poisson_disk_3D_16[16] = vec3[](
    vec3(0.124866500511, -0.00863698819804, -0.341400743366),
    vec3(-0.268977817326, 0.0232703466308, 0.962765739943),
    vec3(-0.926886260514, 0.347145509866, 0.0371667552516),
    vec3(-0.525605917977, -0.83196061317, 0.140450547519),
    vec3(0.769787650906, -0.269987445192, 0.556728356945),
    vec3(0.0277428343064, 0.949913260363, 0.298571144627),
    vec3(0.37483234402, -0.894229404476, -0.157470887791),
    vec3(0.823638399865, 0.511153489846, 0.0112076734743),
    vec3(-0.691697234438, -0.206032134637, -0.669701449126),
    vec3(-0.374049262262, 0.655675135833, -0.653859900948),
    vec3(0.897097829747, -0.250015761047, -0.284058680272),
    vec3(0.414684651809, 0.408980043428, 0.712210796062),
    vec3(0.0894706559412, -0.694165752559, 0.659207203059),
    vec3(0.424163631421, 0.586331878777, -0.652558104146),
    vec3(-0.337585163052, -0.0914606770949, 0.228392827878),
    vec3(-0.0561156256839, -0.641787635508, -0.735946651626)
);

CONST_ARRAY vec3 poisson_disk_3D_32[32] = vec3[](
    vec3(-0.60018987585, -0.37542808789, 0.702422634434),
    vec3(-0.804655452345, -0.505422991675, -0.204321221785),
    vec3(-0.489716407794, -0.312887804229, -0.790139698879),
    vec3(-0.487892879873, -0.786444452486, 0.248902602662),
    vec3(-0.0968247730363, -0.468297170514, -0.301584936252),
    vec3(0.0506288076651, -0.997281894058, 0.0156798074568),
    vec3(0.0370816159214, -0.628016540762, 0.599358604732),
    vec3(0.353342480881, -0.80076061718, -0.417328713504),
    vec3(0.25771681265, -0.448700945256, -0.854720457591),
    vec3(0.302660357014, -0.40465774931, 0.161353254957),
    vec3(0.761655367016, -0.630360560294, -0.0523975145597),
    vec3(0.110135342504, -0.0578890443059, 0.967233278888),
    vec3(0.651672825783, -0.322384521349, 0.676806913396),
    vec3(0.395441071866, -0.0869156202824, -0.325549047628),
    vec3(0.97193068042, 0.158062541275, -0.164458771028),
    vec3(0.83192710037, 0.157410579581, 0.406635006894),
    vec3(0.505787415507, 0.313548120991, -0.799289142807),
    vec3(0.451984918056, 0.42875270527, 0.0105335963486),
    vec3(0.470003613429, 0.632073068978, 0.586594761664),
    vec3(0.211581833164, 0.912089373313, -0.287691333513),
    vec3(0.0219753202213, 0.375795763565, -0.410659254953),
    vec3(-0.145817326565, 0.887109152505, 0.437721196199),
    vec3(-0.298535944277, 0.817380831095, -0.47696102145),
    vec3(-0.026249307315, 0.0437328643958, 0.109145913613),
    vec3(-0.653958747958, 0.751434733869, 0.052527488991),
    vec3(-0.368596873367, 0.385263668821, 0.821284286631),
    vec3(-0.435680921516, 0.373953443926, -0.802394594995),
    vec3(-0.447664776858, 0.340807272232, 0.280608910498),
    vec3(-0.753906082347, 0.506437368124, -0.396948089299),
    vec3(-0.0360074438775, 0.021774171875, -0.987910130891),
    vec3(-0.538616685994, 0.0397711441792, -0.278283776454),
    vec3(-0.896343041093, 0.0625731308449, 0.231223032071)
);


CONST_ARRAY vec3 poisson_disk_3D_64[64] = vec3[](
    vec3(0.0134458752784, 0.0515223838916, 0.568370773936),
    vec3(-0.0831699034937, -0.0536824947606, -0.994002853793),
    vec3(0.957611899576, -0.083657535284, -0.24728035464),
    vec3(-0.271921149023, -0.944190718856, -0.136654821144),
    vec3(-0.084400393783, 0.945492377874, -0.263974317355),
    vec3(-0.969450504612, 0.124813071555, -0.153625208473),
    vec3(0.650264730767, 0.670977386486, 0.253167134805),
    vec3(0.536947714678, -0.722837361038, 0.288886788037),
    vec3(-0.675690887686, -0.474865374251, 0.554053312401),
    vec3(0.391227892814, -0.628131791259, -0.59681058664),
    vec3(-0.600216966104, 0.677940305343, 0.397599190918),
    vec3(0.175600932301, 0.160797117297, -0.245836876184),
    vec3(0.787206112854, -0.0249360571505, 0.5197394831),
    vec3(-0.635474404303, -0.471861728982, -0.572326969195),
    vec3(-0.489943991217, 0.465628619753, -0.671609804297),
    vec3(0.0872336286897, 0.74614911311, 0.642840590914),
    vec3(-0.0315433351207, -0.725169869507, 0.687779980803),
    vec3(-0.302458784625, -0.256083946233, 0.0187286585049),
    vec3(0.540739367962, 0.173680658053, -0.820634732033),
    vec3(0.485182001197, 0.701646337196, -0.387528465579),
    vec3(-0.59244629782, 0.137462300857, 0.789322369309),
    vec3(-0.359783894799, 0.391856473303, -0.0866958866758),
    vec3(-0.877077885357, -0.431731557875, -0.0141262796306),
    vec3(0.0736511584233, 0.546762476554, -0.799579488972),
    vec3(0.38785313343, -0.344135704702, 0.780233776087),
    vec3(0.488065804577, -0.196975300935, 0.0660257142988),
    vec3(0.493165135295, 0.370009795768, 0.768938338393),
    vec3(-0.0963623073576, -0.372012558862, -0.492184985317),
    vec3(0.294731284407, -0.936135763267, -0.155545216295),
    vec3(-0.219875862209, -0.268071722319, 0.936275871621),
    vec3(0.132683181607, 0.601941076002, 0.087976943306),
    vec3(-0.932187153185, -0.0467022197429, 0.358123822153),
    vec3(0.791368281326, -0.574501114567, -0.146033614404),
    vec3(-0.487633492227, 0.0052181454244, -0.432119811391),
    vec3(0.0521779773635, -0.604488937806, 0.181622880159),
    vec3(0.84877565739, 0.393891336669, -0.260334316975),
    vec3(0.401661499043, 0.238155121889, 0.29169943502),
    vec3(0.507590212725, -0.147236786044, -0.417579538195),
    vec3(-0.414251025159, -0.834677475533, 0.31006369073),
    vec3(-0.18574508801, 0.430774114496, 0.879368294104),
    vec3(-0.405250073119, 0.117946582873, 0.339300990799),
    vec3(-0.79330698212, 0.591633311472, -0.0752300553145),
    vec3(-0.208966576507, 0.924622046362, 0.258907981156),
    vec3(-0.0412331309339, -0.827791333558, -0.526033454584),
    vec3(0.362536169883, -0.2449254449, -0.826963802515),
    vec3(-0.231015342989, -0.387092700354, 0.459887166956),
    vec3(0.0715164288616, -0.0490181179047, 0.137274317048),
    vec3(-0.129098120956, 0.225760551654, -0.571066020762),
    vec3(0.175860810113, -0.0088953103939, 0.982731209632),
    vec3(0.91951710405, -0.291814717741, 0.181789804347),
    vec3(0.864855427825, 0.29357483943, 0.182451323036),
    vec3(0.288733135272, -0.499152179756, -0.188908234609),
    vec3(-0.176959074796, 0.497445411795, 0.3845657187),
    vec3(-0.476624606667, 0.804284563972, -0.26395272693),
    vec3(-0.491284678342, 0.0687598759217, -0.865818070666),
    vec3(0.0564623509527, 0.551742718725, -0.357066245652),
    vec3(-0.3567575087, -0.35303135622, -0.851792377991),
    vec3(-0.465899490863, -0.580693154734, -0.207207252224),
    vec3(0.467221476331, 0.388356581843, -0.0854720067221),
    vec3(-0.767963133062, 0.324353934223, 0.241752009357),
    vec3(0.354952779457, 0.921504789807, -0.0532004979549),
    vec3(0.716529688121, -0.439026194247, 0.528033093297),
    vec3(-0.80267475334, 0.257264910241, -0.503441895737),
    vec3(-0.657111462969, -0.0541967353088, 0.0478791817296)
);

