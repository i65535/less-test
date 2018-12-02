'''
Created on 2017-5-11

@author: Administrator
'''
import re
import traceback




def Log(msg):
    with open('log.txt','a') as f:
        f.writelines([msg + '\n'])
        f.flush()

class Html(object):
    def __init__(self, html):
        self.items = self.parse_html(html)
        
    def output(self, filename='class.js'):
        arr = []
        for item in self.items:
            arr.append(str(item))
        
        with open(filename, 'w') as f:
            f.writelines('\n'.join(arr))
        print self.items
        
    def update(self, items):
        self.items.extend(items)
        
    @classmethod
    def parse_html(self, html):
        regex = 'class[ ]*=[ ]*"([\w -]+)"'

        regexobject = re.compile(regex)
        arr = regexobject.findall(html)
        data = []
        last = ''
        for item in arr:
            item = item.strip()
            if last == item:
                continue
            else:
                last = item

            if item.find(' ') == -1:
                data.append(item)
            else:
                data.append(item.split(' '))
        return data
    
    
    def find(self, from_index, key):
        key = key[1:]
        index = 0
        for item in self.items:
            if from_index > index:
                index += 1
                continue
            
            index += 1
            if isinstance(item, basestring):
                if item.strip() == key.strip():
                    return index
            
            for k in item:
                if k.strip() == key.strip():
                    return index
                
        Log('++++++++the class[%s]not exist'%(key))
        return -1
            
        
    
    
        
        
class Css(object):
    def __init__(self, code=None):
        if code is None:
            self.map = {}
        else:
            self.map = self.parse_code(code)
        

    def update(self, code):
        if isinstance(code, Css):
            self.map.update(code.map)
        else:
            data = self.parse_code(code)
            self.map.update(data)

    def parse_code(self, code):
        data = {}
        items = code.split(';')
        for item in items:
            item = item.strip()
            if item:
                arr = item.split(':')
                if len(arr) == 2:
                    data[arr[0].strip()] = arr[1].strip()
                elif len(arr) > 2:
                    index = item.find(':')
                    data[arr[0].strip()] = item[index+1:].strip()
                else:
                    Log('++++++++unexception css [%s]'%(item))
                    
        return data
                
    def to_list(self):
        arr = []
  
        for key, value in self.map.iteritems():
            arr.append('\t%s:%s;'%(key, value))
            
        arr.sort()
        return arr

        

class Style(object):
    
    
    def __init__(self, key, html, index=0):
        self.code = Css()
        self.childs = []
        self.key = key.strip()
        self.html = html
        self.index = html.find(index, self.key) if self.key[0] == '.' else 0
    
    @classmethod
    def split(cls, path):
        path = path.replace('.', ' .').replace(':', ' &:')
        arr = path.split(' ')
        paths = []
        for item in arr:
            item = item.strip()
            if len(item) > 0:
                paths.append(item)
                
        return paths
    
    @classmethod
    def parse_root(cls, txt):
        begin = txt.find('.')
        end = txt.find('{')
        txt = txt[begin:end]
        index1 = txt.find(' ')
        index2 = txt.find('.')
        index = index1 if index1>index2 else index2
        return txt[:index]

    
    def parse(self, paths, code):
        if len(paths) == 0 or  self.key != paths[0]:
            Log('-------------invalid--root-------------')
            return False
        
        if len(paths) == 1:
            self.code.update(code)
            return True
        
        paths.pop(0)
        return self.add_sub_style(paths, code)


        
    def add_sub_style(self, paths, code):
        Log('add_sub_style path=%s'%(str(paths)))
        key = paths[0]
        
        style = self.get_sub_style(key)
        if style:
            if len(paths)==1:
                style.code.update(code)
            else:
                paths.pop(0)
                style.add_sub_style(paths, code)
        else:
            sub_style = Style(key, self.html, self.index)
            if sub_style.parse(paths, code):
                self.childs.append(sub_style)
                
        return True
            
    def get_sub_style(self, key):
        for child in self.childs:
            if child.key == key:
                return child
            
        return None
        
                
            
    def to_less(self, remove=False):
        arr = []
        if remove and self.index < 0:
            return arr
        
        arr.append(self.key + '{')
        arr.extend(self.code.to_list())
        
        self.childs.sort(key=lambda style: style.key)
        
        for child in self.childs:
            items = child.to_less(remove)
            for item in items:
                arr.append('\t%s'%(item))
        arr.append('}')
        return arr
               

def parse_css():
    with open('default.css','r') as f:
        css = f.read()
        
    html = parse_html()
        
    root = Style.parse_root(css)
    if not root:
        Log('parse root fail')
        return
    
    style = Style(root, html)
    items = css.split('}')
    
    for item in items:
        arr = item.strip().split('{')
        if len(arr)==2:
            Log('for key=%s'%(arr[0].strip()))
            
            keys = []
            if arr[0].find(',') > 0:
                keys = arr[0].split(',')
            else:
                keys = [arr[0]]

            for key in keys:
                paths = Style.split(key.strip())
                style.parse(paths, Css(arr[1]))
        else:
            Log('unexception item=[%s]'%(item))
        
    codes = style.to_less(True)
    with open('default.less', 'w') as f:
        f.writelines('\n'.join(codes))
        
    arr = style.to_less()
    with open('default-full.less', 'w') as f:
        f.writelines('\n'.join(arr))



def parse_html():
    with open('index.html','r') as f:
        html = f.read()
        
    return Html(html)
    
    
    
if __name__ == '__main__':
    try:
        parse_css()
    except:
        traceback.print_exc()
        
        
        
        