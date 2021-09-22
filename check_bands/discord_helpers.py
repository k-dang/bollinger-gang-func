def get_options_columns_string(columns):
    final_string = '';
    for i in columns[:-1]:
        final_string += f'{i} | '
    final_string += columns[-1]
    return final_string

def get_options_table_string(values):
    final_string = ''
    for rows in values:
        row_string = ''
        for col in rows[:-1]:
            row_string += f'{str(col)} | '
        row_string += str(rows[-1])
        final_string += f'{row_string} \n'
    return final_string

def get_discord_webhook_body():
    webhook_body = {
        'embeds': [
            {
                'fields': []
            }
        ]
    }
    return webhook_body

def get_empty_discord_webhook_body(title):
    webhook_body = {
        'embeds': [
            {
                'title': title
            }
        ]
    }
    return webhook_body