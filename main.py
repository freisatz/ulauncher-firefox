from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, SystemExitEvent,PreferencesUpdateEvent, PreferencesEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from history import FirefoxHistory

import re
import urllib.parse

class FirefoxHistoryExtension(Extension):
    def __init__(self):
        super(FirefoxHistoryExtension, self).__init__()
        #   Firefox History Getter
        self.history = FirefoxHistory()
        #   Ulauncher Events
        self.subscribe(KeywordQueryEvent,KeywordQueryEventListener())
        self.subscribe(SystemExitEvent,SystemExitEventListener())
        self.subscribe(PreferencesEvent,PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,PreferencesUpdateEventListener())

class PreferencesEventListener(EventListener):
    def on_event(self,event,extension):
        #   Aggregate Results
        extension.history.aggregate = event.preferences['aggregate']
        #   Results Order
        extension.history.order = event.preferences['order']
        #   Results Number
        try:
            n = int(event.preferences['limit'])
        except:
            n = 10
        extension.history.limit = n
        
class PreferencesUpdateEventListener(EventListener):
    def on_event(self,event,extension):
        #   Results Order
        if event.id == 'order':
            extension.history.order = event.new_value
        #   Results Number
        elif event.id == 'limit':
            try:
                n = int(event.new_value)
                extension.history.limit = n
            except:
                pass
        elif event.id == 'aggregate':
            extension.history.aggregate = event.new_value

class SystemExitEventListener(EventListener):
    def on_event(self,event,extension):
        extension.history.close()

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query  = event.get_argument()
        #   Blank Query
        if query == None:
            query = ''
        items = []
        
        #    Open website        
        m = re.match("^(?:([a-z-A-Z]+)://)?([a-zA-Z0-9/-_]+\.[a-zA-Z0-9/-_\.]+)(?:\?(.*))?$", query)
        protocol = "https"
        url = ""
        if m:
            if m.group(1):
                protocol = m.group(1)
            base = m.group(2)
            params = m.group(3)
            encoded = f"?{urllib.parse.quote(params)}" if params else ""
            url = f"{protocol}://{base}{encoded}"
        
            items.append(ExtensionResultItem(icon='images/icon.png',
                                                    name="Open URL",
                                                    description=url,
                                                    on_enter=OpenUrlAction(url)))
            
        #   Search into Firefox History
        results = extension.history.search(query)
        for link in results:
            #   Encode 
            hostname = link[0]
            #   Split Domain Levels
            dm = hostname.split('.')
            #   Remove WWW
            if dm[0]=='www':
                i = 1
            else:
                i = 0
            #   Join remaining domains and capitalize
            name = ' '.join(dm[i:len(dm)-1]).title()
            #   TODO: favicon of the website
            if extension.history.aggregate == "true":
                items.append(ExtensionResultItem(icon='images/icon.png',
                                                name=name,
                                                on_enter=OpenUrlAction('https://'+hostname)))
            else:
                if link[1] == None:
                    title = hostname
                else:
                    title = link[1]
                items.append(ExtensionResultItem(icon='images/icon.png',
                                                name=title,
                                                description=hostname,
                                                on_enter=OpenUrlAction(hostname)))

        return RenderResultListAction(items)

if __name__ == '__main__':
    FirefoxHistoryExtension().run()
