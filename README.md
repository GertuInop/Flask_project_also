!["Обзор"](src/static/pictures/20240522224535.png)
# WEB-приложение "Обзор"
 ## Описание
 
 Мой проект - это создание WEB-приложения, который посвящён для публикации своего мнения о прочитанной книге. 

## Установка программы
 Перед установкой программы, вам нужно убедиться, что у вас установлен **язык программирования - Python3**. Если у вас его нет, то вы можете установить Python на официальном сайте: https://www.python.org/downloads/

Чтобы проверить, учтановлени ли у вас Python вам нужно написать его версию в командную строку:


 ```
    python --version
 ```
 
 ### Процедура установики программы:

 1. Вам нужно загрузить все файлы из папки "src" к себе на компьютер в отдельную папку;
 2. Далее вам нужно открыть командную строку и прописать там путь в вашу папку:
 ```
    cd <папка1>\<папка2>\<папка с проектом>
 ```
 3. После вам нужно установить образ вашего проекта. Для этого пропишите следующее:
 ```
    docker build .
 ```
 4. После установки образа вы можете его переименовать, чтобы было легче запускать проект. Делается это следующим обраом:
 ```
    docker build -t <название образа> .
 ```

 Поздравляю! Вы успешно уставноили проект "Обзор".
 ## Использование
 Чтобы запустить проект, нужно прописть одну строку в CMD:
 ```
    docker run -p 5000:5000 <название образа>
 ```
 ## Разработка
 Если у вас есть какаие-то идеи, которые могут улучшить проект, или вы нашли какие-либо ошибки, то можете отправить письмо на почту, указанную в профиле.
 ## Участники
 Разработчиком проекта является студент колледжа ГБПОУ колледжа "Царицыно" Семенов Иван.
