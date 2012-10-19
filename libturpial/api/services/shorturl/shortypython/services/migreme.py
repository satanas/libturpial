## Author: Oswaldo Gama Júnior aka @gama_jr
## Migre.me support
## Date: 18/10/2012

## 
class Migreme(Service):

    def shrink(self, bigurl):
        resp = request('http://migre.me/api.txt', {'url': bigurl})
        return resp.read()

