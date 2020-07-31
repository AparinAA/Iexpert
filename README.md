# Iexpert
Для простоты используем ветку master, так как работаем над проектом в двоем

0. Установить git.
1. *git clone https://github.com/AparinAA/Iexpert.git .* В дирикторию, в которой выполнили команду, подтягиваются файлы с github. (Создается папка Iexpert, если хотим в свою папку сохранить, то можно добавить *git clone https://github.com/AparinAA/Iexpert.git myfolder*).
2. Работаем в текущей dir. Там создается невидимый файл \*.git.
3. Вносим изменения в директорию
4. Для добавления изменений
```
   git add
   git commit -m "Комментарий по изменению файлов"
   git push origin master
```
**Если кто-то загрузил изменения**
Если мы отправим изменения *git push origin master*, то получим ошибку.\
Для начала нужно скачать коммит с исправленным файлом, а затем их локально слить со своими:
```
   git fetch origin
   git merge origin/master
```
*Здесь скачались изменения от другого пользователя и теперь проверяем не сломался ли наш код*
```
git add .
git commit -m "comment"
git push origin master
```
5. Работа на удаленном сервере с соеденением SSH:
+ Подключить виртуальную среду 
```
   source ~/djangoenv/bin/activate
```
+ Зайти в директорию с проектом 
```
   cd ~/www/expert-olymp.ru/Iexpert
```
+ Перезапустить сервер
```
   rm ~/www/expert-olymp.ru/tmp/restart.txt
   vi ~/www/expert-olymp.ru/tmp/restart.txt
```
+ Загрузить обновления из git 
```
   git pull
```
+ Если ругается при слияние
```
   git fetch --all
   git reset --hard origin/master
   git pull
```
