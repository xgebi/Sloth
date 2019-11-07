# Toes language


## Importing files

`<toe:import file="header.html" />`

This tag imports files that are located in the same folder or in subfolders.

Attribute `file` points to the location of imported file.

## Working with variables

`<toe:create var="name" value="value" />`

`toe:create` will create new variable in current scope with provided value which is not optional.

`<toe:assign var="name" value="value" />`

`toe:assign` will assign value to variable which is located in current or any parent scope.

### Modifiers

`<toe:modify var="name" toe:add="number" />`

`toe:add` will add number to variable `name`

*Note:* attributes of `toe:modify` used below will produce an error if variable isn't a number.

`<toe:modify var="name" toe:inc />`

`toe:inc` will increment variable by 1.

`<toe:modify var="name" toe:dec />`

`toe:dec` will decrement variable by 1.

`<toe:modify var="name" toe:sub="number" />`

`toe:sub` will subtract number from variable `name`.

`<toe:modify var="name" toe:mul="number" />`

`toe:mul` will multiply variable `name` by number.

`<toe:modify var="name" toe:div="number" />`

`toe:div` will divide variable `name` by number.

`<toe:modify var="name" toe:mod="number" />`

`toe:mod` will produce remainder after division by `number`.

`<toe:modify var="name" toe:pow="number" />`

`toe:pow` will create number which is equal to variable value to specified power.



## Control structures

### `if` control structure

`<tag toe:if="expression">`

`if` control structure helps to display nodes if certain condition is met. Currently there is no `toe:else` node. `else` clause can simulated by using `not expression`.

Values such as `True` or `3 > 2` are not allowed. On the other hand values such as `False` or `3 < 2` are allowed because they won't do any damage.

### `for` loop

`<tag toe:for="expression">`

In this implemetation of `for` loop syntax for the expression is `item in items`. Where `items` needs to be a list, a set, a tuple or a sequence.

Warning: `item` (or different name defined in the expression) will be created in `for` loop's variable scope. In case you need to access variable in parent scope to for loop's you need to go through `parent.variable_name`.

### `while` loop

`<tag toe:while="expression">`

`while` loop in Toe language accepts either an instance of `Iterable` object or a condition which has to have on at least one side variable.

Values such as `True` or `3 > 2` are not allowed. On the other hand values such as `False` or `3 < 2` are allowed because they won't do any damage.

## Modifying content inside of tags

`<tag toe:value="value" />`

Assigns `value` to input tags, e. g.  `<input toe:value="variable" />` will result into `<input value="variable_value" />`

`<tag toe:attr-[attribute name]="value" />`

Will create an attribute on tag if it doesn't already exists and will assign `value` to that attribute.

`<tag toe:content="value" />`

Replaces text content of tag/node with `value`. 

`<tag toe:computed-value="value" />`

TBD

`<tag toe:computed-attr-[attribute name]="value" />`

TBD

`<tag toe:computed-content="value" />`

TBD