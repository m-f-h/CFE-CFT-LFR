
#@title `do_menu()` : afficher un menu, attendre un choix, et exéctuer actions

def do_menu(menu:dict, greeting: str = '', **data):
    """Affiche le `greeting` (en-tête) (si fourni) et le menu,
attend l'un des choix proposés, et execute l'action correspondante.
`menu` est un dict { choix: action } ou les `choix` sont `int` ou `str`
et les `action` sont des fonction dont le docstring est affiché dans le menu,
en utilisant `data` pour substituer d'éventuelles `{variables}` dans les docstrings."""
    while True:
      if greeting: display(greeting, clear = True)
      for var in data: data[var] = globals().get(var, data[var]) # update data
      for choix, action in menu.items():
          print(f"({choix}) -", action.__doc__.format( **data ))
      time.sleep(1)
      while True:
          print("Votre choix : ")
          if (i := input().strip()) in menu or i.isdigit() and (i := int(i))in menu:
              break
          display(HTML("Veuillez entrer un des choix proposés!"))
      if menu[i]()=='return': return
