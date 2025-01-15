# Broken-audio-sound-generator-python-(Version-1)

And in short, such a bombastic idea came to my mind. I don't know if I'm the first to do this on the planet, but figure out what it would be like to take a video and break up a mosaic of bits in the video, and in short, assemble these bits back into the video by randomly mixing them together like mosaics, and how such a generator would turn out. random broken videos... And in short, I wrote this code, but it doesn't work with all videos, but it works fine with audio.

1) In the select_video_to_bytes() function, shuffle an array of bytes using random.shuffle().

2) The shuffled bytes are converted back to the bytes object.

And anyway, I did it with a couple of music tracks, and that's what I got.:

https://disk.yandex.ru/d/0ToC8ynmL-8yGQ

At 0:20, you can clearly hear "Save us!" at 0:40 "Forgive us!" at 0:52 "Vazgen!" 01:08 "You're different" what's that like... 01:17 "Let us go" at 01:28 Pussy dash? 02:08 Are you normal? 02:12 calm down... 02:31 who are you? 02:38 What's the deal!? 02:45 Ira!

This audio track is based on KSHMR_Marnik__Bazaar_Officiel_Sunburn_Goa_2015_Anthem_EDM

There is an idea to improve the video by mixing not the bits in the video, but by splitting them into a random sequence of tiles, say from 1 to 10 bits, and then you can achieve a more effective result, I think...

# Broken-audio-sound-generator-python-(Version-2)

Here is the second version, which is good in its own way... Only some sequences are half mixed, and some are not mixed and then mixed together in audio, but it does not work with video.

1) Now 80% of the bytes are shuffled (you can change this value), leaving the remaining 20% in their original position to preserve video playback.

2) The array of shuffled bytes is combined with the unmixed bytes, which allows you to play the video without errors.
