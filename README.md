# Конструктор интерактивных инструкций
Новостной tg канал: https://t.me/ii_constructor

Конструктор интерактивных инструкций — это ПО, предназначенное для упрощённого создания чат-ботов.

Конструктор интерактивных инструкций — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

Конструктор интерактивных инструкций распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>.

## Как получить тестовую версию
Сейчас проект в стадии разработки и ещё не достиг MVP, но кое-что уже работает. Чтобы получить исполняемый файл редактора и готовый движок в текущей стадии разработки, свяжитесь с разработчиком: @mikolainer ( vk / telegram / whatsapp ) или по почте (mikolainer@mail.ru).

Заинтересованным разработчикам смотреть раздел "Как запустить".

## Описание
Система состоит из двух частей:
- редактор сценария;
- движок бота.

Обе части предназначены для взаимодействия со сценарием: редактор - для создания, описания и размещения в БД, а движок - для интеграции с мессенджерами и прочими платформами для взаимодействия с пользователем.

## Сценарий
Сценарий представляет собой машину состояний.

### Состояния
У каждого состояния есть id и имя. Если имя не указано, оно будет соответствовать строковому представлению идентификатора.

Каждое состояние связано с ответом который получит пользователь, попадая в него. Сейчас ответом может быть только обычный плоский текст, но планируется введение поддержки специфических для платформ дополнений (кнопки/карточки и т.д)

Есть особый тип состояний (см. "Точки входа").

### Управляющее воздействие
Сейчас управляющее воздействие описывается набором синонимов. В перспективе могут добавиться другие типы управляющих воздействий, например кнопки или вектора для классификации нейросетями.

Каждое управляющее воздействие имеет уникальное имя.

### Переходы
Каждый переход между состояниями связан с одним управляющим воздействием.

Переходы также связаны со "связями". Таким образом "связь" определяет направление перехода (откуда и куда) и может объединять в себе несколько "переходов" связанных с управляющими воздействиями.

Есть особый тип переходов (см. "Точки входа").

### Точки входа
Кроме обычных состояний и переходов есть "точки входа". Точка входа - "связь" между состояниями, которая определяет только "куда", но не "откуда". Это значит, что в это состояние "куда" можно перейти по соответствующему управляющему воздействию из любого другого состояния.

Для состояний и переходов точек входа есть ограничения:
- Единственное управляющее воздействие, которое может быть связано с точкой входа, должно иметь такое же имя как у состояния-входа;
- У состояния-входа должно быть уникальное имя;
- Нельзя переименовать или удалить состояние-вход.

существуют обязательные точки входа, которые нельзя удалить или переименовать.

## Движок
Сейчас движок - это zip архив с кодом на python, готовый для загрузки на яндекс-клаудфункцию и интеграции с Яндекс диалогами. В перспективе планируется сделать self-hosted версию и поддержку Telegram.

см. "Как получить тестовую версию" или "Как запустить"

## Редактор
Сейчас редактор сценария - это приложение для Windows. Linux номинально поддерживается, но фактически не дебажился.

Здесь вы сможете:
- создать сценарий в оперативной памяти и сохранить его в файл;
- открыть сценарий из файла;
- подключиться к БД и создать сценарий там или загрузить из сохранённого файла;
- протестировать сценарий внутренним эмулятором чата с ботом.

## Описание интерфейса
### Главное окно
Главное окно программы содержит туллбар с кнопками основных функциональных возможностей приложения ("Новый проект", "Открыть проект", "Сохранить проект", "Подключиться к БД", "Список синонимов" и "Тестировать").

Чтобы создалась рабочая область, нужно открыть или создать проект соответствующей кнопкой в туллбаре ("Открыть проект" или "Новый проект").

### Редактор синонимов
Для управления наборами синонимов можно открыть редактор синонимов по кнопке "Список синонимов" в туллбаре главного окна.

Обратите внимание, что набор управляющих воздействий у каждого сценария свой. Поэтому это окно можно открыть только при открытом проекте.

Здесь слева отображается список существующих групп синонимов, а справа список синонимов выбранной в левой части группы синонимов.

### Эмулятор чата
Для тестирования открытого сценария вы можете воспроизвести поведение сценария в окне тестирования. Его можно открыть по кнопке "Тестировать" в туллбаре главного меню.

### Рабочая область
Рабочая область главного окна разделена на 2 части: слева находится список точек входа, а справа - вкладки с графическими сценами представления сценария.

По нажатию кнопки "+" в списке точек входа включается режим добавления точек входа. Чтобы выйти из этого режима, нажмите esc.
В режиме создания точки входа можно выбрать существующее состояние, чтобы сделать его точкой входа, или дважды кликнуть по сцене в пустом месте, чтобы создать новое состояние-вход.

Если навести на кнопку "+" состояния на сцене, она немного сместится и за неё можно будет потянуть, чтобы создать переход. Чтобы создать новое состояние, бросьте стрелку в пустом месте сцены, а чтобы добавить переход в существующее состояние, бросьте стрелку над существующим состоянием.

### Работа с БД
Если вам доступна развёрнутая БД, можно к ней подключиться через соответствующий диалог. Диалог подключения к БД открывается, пока БД ещё не подключена по нажанию кнопки "Подключение к БД".
После успешного подключения по этой кнопке будет открываться диалог работы с БД, в котором можно создать новый сценарий в БД, загрузить в БД сценарий из файла или открыть существующий в БД сценарий.

### Разворачивание на клаудфункции
- загрузите сценарий в БД
- получите движок
- создайте клаудфункции
- загрузите код движка в клаудфункцию
- укажите точку входа `index.handler`
- укажите переменные окружения: `SCENARIO_ID`, `IP`, `PORT`, `USER`, `PASSWORD`

## Как запустить
Для начала работы:
- Убедитесь, что у вас установлен python;
- Склонируйте репозиторий и запустите скрипт `setup_venv.bat`. Это создаст виртуальное окружение и установит пакеты из папки `ii_constructor\packages`.

Если вы используете VSCode:
- настройтке `.vscode\launch.json` так, чтобы запускался файл `ii_constructor/apps/qteditor/__main__.py`;
- добавьте в `.vscode\settings.json` ключ `"python.analysis.extraPaths"` со списком путей к пакетам в качестве значения:
```
    [
        "./ii_constructor/packages/levenshtain",
        "./ii_constructor/packages/inmemoryrepo",
        "./ii_constructor/packages/mariarepo",
        "./ii_constructor/packages/mysqlrepo",
        "./ii_constructor/packages/gui",
        "./ii_constructor/packages/core"
    ]
```
- ознакомьтесь с `ii_constructor\doc\UML.svg` (эта диаграмма может не вполне соответствовать последним изменениям в коде, но покажет основные сущности программы и их взаимосвязь).

Работа с БД:
- чтобы создать БД (в СУБД mariadb или mysql), используйте `ii_constructor\db\ii_constructor.sql`
- чтобы сформировать движок, запустите скрипт `make_db_engine.bat`. После этого упакуйте в zip архив содержимое папки `engine`.

### Разработка конструктора
- Установите зависимости для разработки из `requirements-dev.txt`:
  ```
  pip install -r requirements-dev.txt
  ```
- После изменения кода посмотрите предложения линтеров:
  ```
  black --diff .
  isort --dif .
  ruff check .
  ```
- Исправтье код автоматически и самостоятельно:
  ```
  black .
  isort .
  ruff check --fix .
  ```
