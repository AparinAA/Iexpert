# Iexpert
Пока будем использовать ветку *master* для локального тестирования (потом добавлю ветку для релиза)

0. Установить git.
1. *git clone https://github.com/AparinAA/Iexpert.git .* В дирикторию, в которой выполнили команду, подтягиваются файлы с github. (Создается папка Iexpert, если хотим в свою папку сохранить, то можно добавить *git clone https://github.com/AparinAA/Iexpert.git myfolder*).
2. Работаем в текущей dir. Там создается невидимый файл \*.git.
3. Вносим изменения в директорию\ 
4. Для добавления изменений\
*git add .*\
*git commit -m "Комментарий по изменению файлов"*\
*git push origin master*\
**Если кто-то загрузил изменения**\
*git add .*\
*git commit -m "comment"*\
Теперь, если мы отправим изменения *git push origin master*, то получим ошибку.\
Для начала нужно скачать коммит с исправленным файлом, а затем их локально слить со своими:\
*git fetch origin*\
*git merge origin/master*\
*проверяем не сломался ли наш код*\
*git push origin master*
