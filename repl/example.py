from repl import repl

def prepare_food():
    print("Okay, %s is on the way!" % food)

def cook_sandwich():
    global food
    food = 'sandwich'
    prepare_food()

def cook_milkshake():
    global food
    food = ' milkshake'
    print("What flavour do you want?")
    yield '1', 'Strawberry', strawberry_milkshake
    yield '2', 'Chocolate', confirm_chocolate

def strawberry_milkshake():
    global food
    food = 'strawberry' + food
    prepare_food()

def confirm_chocolate():
    print("Are you sure you want a chocolate milkshake? (it's very sweet)")
    yield 'y', 'yes', chocolate_milkshake
    yield 'n', 'no', cook

def chocolate_milkshake():
    global food
    food = 'chocolate' + food
    prepare_food()

def cook():
    print("What do you want to order?")
    yield '1', 'Sandwich', cook_sandwich
    yield '2', 'Milkshake', cook_milkshake

repl(cook)
