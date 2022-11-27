class DiscordEmbedField(object):
    name: str
    value: any
    inline: bool = False
    
    def __init__(self, name: str, value: any, inline: bool = False) -> None:
        self.name = name
        self.value = value
        self.inline = inline
    

class DiscordEmbed(object):
    title: str
    description: str
    fields: list[DiscordEmbedField]
    
    def __init__(self, title: str, description: str, fields: list[DiscordEmbedField] = None) -> None:
        self.title = title
        self.description = description
        if fields is None: 
            fields = list()
        self.fields = fields
    
    def add_field(self, field: DiscordEmbedField) -> None:
        self.fields.append(field)
    
    def __dict__(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "fields": [field.__dict__ for field in self.fields]
        }


class DiscordMessage(object):
    content: str
    embeds: list[DiscordEmbed]
    
    def __init__(self, content: str, embeds: list[DiscordEmbed] = None) -> None:
        self.content = content
        if embeds is None:
            embeds = list()
        self.embeds = embeds
    
    def add_embed(self, embed: DiscordEmbed) -> None:
        self.embeds.append(embed)
    
    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "embeds": [embed.__dict__() for embed in self.embeds]
        }