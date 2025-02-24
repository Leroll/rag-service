# 为了兼容23年接口，做的复制




from __future__ import unicode_literals

import codecs
import re
import time
import warnings

import six

import requests

__version__ = '0.0.27'



end_of_field = re.compile(r'\r\n\r\n|\r\r|\n\n')


class SSEClient(object):
    def __init__(self, url, data, last_id=None, retry=3000, session=None, chunk_size=10000, **kwargs):
        self.url = url
        self.last_id = last_id
        self.retry = retry
        self.chunk_size = chunk_size
        self.data = data
        
        
        self.session = session
        
        
        self.requests_kwargs = kwargs
        
        
        if 'headers' not in self.requests_kwargs:
            self.requests_kwargs['headers'] = {}
        self.requests_kwargs['headers']['Cache-Control'] = 'no-cache'
        
        
        self.requests_kwargs['headers']['Accept'] = 'text/event-stream'
        
        
        self.buf = ''
        
        self._connect()
        
    def _connect(self):
        if self.last_id:
            self.requests_kwargs['headers']['Last-Event-ID'] = self.last_id
            
        
        requester = self.session or requests
        
        self.resp = requester.post(self.url, json=self.data, stream=True, **self.requests_kwargs)
        self.resp_iterator = self.resp.iter_content()
        encoding = self.resp.encoding or self.resp.apparent_encoding or 'utf-8'
        self.decoder = codecs.getincrementaldecoder(encoding)(errors='replace')
        
        
        
        self.resp.raise_for_status()
        
    def iter_content(self):
        def generate():
            while True:
                if hasattr(self.resp.raw, '_fp') and \
                    hasattr(self.resp.raw._fp, 'fp') and \
                    hasattr(self.resp.raw._fp.fp, 'read1'):
                    chunk = self.resp.raw._fp.fp.read1(self.chunk_size)
                else:
                    
                    
                    
                    chunk = self.resp.raw.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
            
        return generate()
    
    def _envent_complete(self, line):
        return re.search(end_of_field, self.buf) is not None
    
    def __iter__(self):
        return self
    
    def __next__(self):
        while not self._envent_complete():
            try:
                next_chunk = next(self.resp_iterator)
                if not next_chunk:
                    raise EOFError()
                self.buf += self.decoder.decode(next_chunk)
                
            except (StopIteration, requests.RequestException, EOFError, six.moves.http_client.IncompleteRead) as e:
                print(e)
                time.sleep(self.retry / 1000.0)
                self._connect()
                
                
                
                head, sep, tail = self.buf.rpartition('\n')
                self.buf = head + sep
                continue
            
        
        
        
        (event_string, self.buf) = re.split(end_of_field, self.buf, maxsplit=1)
        msg = Event.parse(event_string)
        
        
        if msg.retry:
            self.retry = msg.retry
            
            
        
        if msg.id:
            self.last_id = msg.id
            
        return msg
    
    if six.PY2:
        next = __next__
        

class Event(object):
    
    sse_line_pattern = re.compile('(?P<name>[^:]*):?( ?(?P<value>.*))?')
    
    def __init__(self, data='', event='message', id=None, retry=None):
        assert isinstance(data, six.string_types), "Data must be text"
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry

    def dump(self):
        lines = []
        if self.id:
            lines.append('id: %s' % self.id)
        
        
        if self.event != 'message':
            lines.append('event: %s' % self.event)
        
        if self.retry:
            lines.append('retry: %s' % self.retry)
        
        lines.extend('data: %s' % d for d in self.data.split('\n'))
        return '\n'.join(lines) + '\n\n'
    
    @classmethod
    def parse(cls, raw):
        
        
        
        
        msg = cls()
        for line in raw.splitlines():
            m = cls.sse_line_pattern.match(line)
            if m is None:
                
                warnings.warn('Invalid SSE line: "%s"' % line, SyntaxWarning)
                continue
            
            name = m.group('name')
            if name == '':
                
                continue
            value = m.group('value')
            
            if name == 'data':
                
                
                if msg.data:
                    msg.data = '%s\n%s' % (msg.data, value)
                else:
                    msg.data = value
            elif name == 'event':
                msg.event = value
            elif name == 'id':
                msg.id = value
            elif name == 'retry':
                msg.retry = int(value)
            
        return msg
    
    def __str__(self):
        return self.data