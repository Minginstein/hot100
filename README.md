# hot100: An Analysis of Billboard's Hot 100 since 1958

## Purpose:
Explore Python based data pipeline and analysis libraries via an interesting domain. 

## Contents
* ocr (Deprecated): Contains modules dedicated to collection of "monthly listeners" data point in .png format. I used Sikuli, Tesseract, a CNN
based approach to transcription.

## Key research questions:
* How have the audio features of the Hot 100 evolved over time?
 * Is it possible to map the emergence of popular genres via Spotify Audio Features?
* Which artists have achieved longevity on Spotify?
 *Is it possible to model an artist's longevity as a function of their choices in musical production?
 
## Core Learnings
### Automation Is Fragile
If a company does not want you to see something, don't attempt to automate its retrieval :) When I started the project, 
I was very focused on the "monthly listeners" stat which Spotify does not expose via the web API. It's a supremely interesting
metric, one which I used in a previous job. Until recently this stat was only available in .png via the Spotify Desktop 
application. I was able to cobble something together to extract it using GUI Automation (Sikuli) and OCR. _But is it really 
automation if a simple color change would break the whole pipeline?_ 

Ironically, Spotify later exposed this data point via the web application.
See https://xkcd.com/1319

## Data sources:
* Billboard Hot 100 archives (http://www.billboard.com/archive/charts)
* Spotify Web API (https://developer.spotify.com/web-api/)
* Spotify Web Player

## License
All material in this repository is made available under the [Creative Commons Attribution license](https://creativecommons.org/licenses/by/4.0/). The following is a human-readable summary of (and not a substitute for) the [full legal text of the CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/legalcode).
