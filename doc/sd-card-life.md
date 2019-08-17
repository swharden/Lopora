# Lifetime of SD Cards

### The problem (described by an expert)

_Flash memory indeed has limited write cycles. However, by now it is unlikely that you'll encounter this within the normal lifetime of such a card. Usually this is in the order of 10,000 write cycles for an MLC today and SD cards include circuitry to manage wear-leveling, that is, spread out writes over the storage media evenly to avoid "hot spots": pages that are written too frequently and therefore failing early._

_Many FLASH micro-controller applications are failing after 5-10 years because of FLASH memory corruption. Re-FLASHing the firmware restores the chip for another 5-10 years etc. So you must refresh FLASH memory data periodically to ensure continued integrity. Same would apply if you wanted to use the SD card as long term storage._

### Lopora Disk Usage
I have a 32 GB SD card, MLC from SanDisk for only 15 euros. 
The free memory is approximately 20 GB, the rest is in use for the operating system and NOOBs. 
Lopora writes approximately 10MB/hour to this SD card. Writings are spread out over 20GB.
Calculation:
10MB/hour: 20GB / 10MB = 2000 hours = 83 days. 
So it takes 83 days to write all the memory locations once. 
That means that every year every memory location will be written 4.4x.
The life time is 10,000 cycles, so it will take 10,000/4.4 = 2270 years before the maximum number of readings will be exceeded!!!
However, when you want to use 3 grabbers, this life time will be 2270 / 3 = 750 years.

### Conclusion
So to be at the very safe side, I would recommend to buy a new SD card every 200 years!!! 
Or every 5 years if you do not refresh the SD card...

