# Linux-palvelimet – Week 4

## Tehtävän kuvaus

Tässä tehtävässä toteutettiin kahden Ubuntu-palvelimen välinen MariaDB-tietokannan replikointi sekä automaattinen varmuuskopiointi rsync-ohjelmalla.

Toteutuksessa on kaksi palvelinta:

| Palvelin | Julkinen IP | Tehtävä |
|---|---|---|
| Server A | `193.166.25.4` | Pääpalvelin, joka vastaanottaa laskurin päivitykset |
| Server B | `86.50.231.166` | Replikointipalvelin, joka näyttää pääpalvelimen laskuriarvon |

## Palvelimien verkkosivut

- [Server A – Week 4](http://193.166.25.4/viikko4/)
- [Server B – Week 4](http://86.50.231.166/viikko4/)

Server A kasvattaa laskurin arvoa sivua avattaessa. Server B näyttää tietokannan replikoidun arvon eikä itse kasvata laskuria.



## Automaattinen varmuuskopiointi

Server B suorittaa tunnin välein rsync-varmuuskopioinnin Server A:n hakemistosta.

Varmuuskopiot tallennetaan Server B:ssä hakemistoon:


Jokainen varmuuskopio tallennetaan omaan aikaleimalla nimettyyn hakemistoonsa.


## Käytetyt palvelut ja ohjelmistot

- Ubuntu Server 24.04
- MariaDB
- Nginx
- Python ja Flask
- Gunicorn
- PyMySQL
- rsync
- cron
- systemd

## Palveluiden käynnistyminen

Molemmilla palvelimilla keskeiset palvelut on määritetty käynnistymään automaattisesti:

- MariaDB
- Nginx
- Week 4 Flask-sovellus

Server B:ssä myös cron suorittaa ajastetun varmuuskopioinnin.

