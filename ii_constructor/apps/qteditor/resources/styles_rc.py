# Copyright 2024 Николай Иванцов (tg/vk/wa: <@mikolainer> | <mikolainer@mail.ru>)
# Copyright 2024 Kirill Lesovoy
# 
# Этот файл — часть "Конструктора интерактивных инструкций".
# 
# Конструктор интерактивных инструкций — свободная программа:
# вы можете перераспространять ее и/или изменять ее на условиях
# Стандартной общественной лицензии GNU в том виде,
# в каком она была опубликована Фондом свободного программного обеспечения;
# либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.
# Конструктор интерактивных инструкций распространяется в надежде,
# что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ;
# даже без неявной гарантии ТОВАРНОГО ВИДА
# или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ.
# Подробнее см. в Стандартной общественной лицензии GNU.
# 
# Вы должны были получить копию Стандартной общественной лицензии GNU
# вместе с этой программой. Если это не так,
# см. <https://www.gnu.org/licenses/>.





from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x04t\
M\
ainWindow{\x0d\x0a    \
background-color\
: #74869C;\x0d\x0a}\x0d\x0a\x0d\
\x0aMainToolButton{\
\x0d\x0a    background\
-color: #59A5FF;\
\x0d\x0a    border-rad\
ius: 32px;\x0d\x0a}\x0d\x0a\x0d\
\x0aMainToolButton#\
Close{\x0d\x0a    back\
ground-color: #F\
F3131;\x0d\x0a    bord\
er-radius: 4px;\x0d\
\x0a    border: non\
e;\x0d\x0a}\x0d\x0a\x0d\x0aCloseBu\
tton{\x0d\x0a    backg\
round-color: #FF\
3131;\x0d\x0a    borde\
r: 0px;\x0d\x0a    bor\
der-radius: 10px\
;\x0d\x0a}\x0d\x0a\x0d\x0aFlowWidg\
et {\x0d\x0a    backgr\
ound-color: #DDD\
DDD;\x0d\x0a    border\
: 1px solid blac\
k;\x0d\x0a}\x0d\x0a\x0d\x0aQScroll\
Area{\x0d\x0a    backg\
round-color: #FF\
FFFF;\x0d\x0a    borde\
r: none;\x0d\x0a}\x0d\x0a\x0d\x0aQ\
ScrollArea[isNod\
eContent=true]{\x0d\
\x0a   border: 0px;\
\x0d\x0a   border-top:\
 1px solid #59A5\
FF;\x0d\x0a   border-b\
ottom-right-radi\
us: 10px;\x0d\x0a   bo\
rder-bottom-left\
-radius: 10px;\x0d\x0a\
   background-co\
lor: #FFFFFF;\x0d\x0a}\
\x0d\x0a\x0d\x0aQWidget[isWi\
ndowTitle=true]{\
\x0d\x0a    background\
-color : #666;\x0d\x0a\
}\x0d\x0a\x0d\x0aQWidget[isN\
odeTitle=true]{\x0d\
\x0a   border: 0px;\
\x0d\x0a   border-top-\
right-radius: 10\
px;\x0d\x0a   border-t\
op-left-radius: \
10px;\x0d\x0a   backgr\
ound-color: #666\
666;\x0d\x0a}\x0d\x0a\x0d\x0aNodeT\
itle{\x0d\x0a   color:\
 #FFFFFF;\x0d\x0a}\x0d\x0a\x0d\x0a\
SynonymsGroupWid\
get{\x0d\x0a    backgr\
ound-color: #FFF\
FFF;\x0d\x0a    border\
: 2px solid #FFF\
FFF;\x0d\x0a}\x0d\x0a\x0d\x0aQLine\
Edit[SynonymEdit\
or=true]{\x0d\x0a    b\
ackground-color:\
 #FFFFFF;\x0d\x0a    b\
order: 2px solid\
 black;\x0d\x0a    bor\
der-radius: 5px;\
\x0d\x0a}\
"

qt_resource_name = b"\
\x00\x06\
\x07\xac\x02\xc3\
\x00s\
\x00t\x00y\x00l\x00e\x00s\
\x00\x09\
\x0d\xf7\xbdC\
\x00l\
\x00i\x00g\x00h\x00t\x00.\x00q\x00s\x00s\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x12\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\x92O\x06\x85d\
"


def qInitResources():
    QtCore.qRegisterResourceData(
        0x03,
        qt_resource_struct,
        qt_resource_name,
        qt_resource_data,
    )


def qCleanupResources():
    QtCore.qUnregisterResourceData(
        0x03,
        qt_resource_struct,
        qt_resource_name,
        qt_resource_data,
    )


qInitResources()  # FIXME: Убрать вызов в __main__.py
