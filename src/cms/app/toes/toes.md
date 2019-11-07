# Toes language


## Importing files

`<toe:import file="header.html" />`

This tag imports files that are located in the same folder or in subfolders.

Attribute `file` points to the location of imported file.

## Working with variables

`<toe:assign var="name" value="value" />`

`<toe:modify var="name" toe:inc />`

`<toe:modify var="name" toe:dec />`

`<toe:modify var="name" toe:add="number" />`

`<toe:modify var="name" toe:sub="number" />`

`<toe:modify var="name" toe:mul="number" />`

`<toe:modify var="name" toe:div="number" />`

`<toe:modify var="name" toe:mod="number" />`

`<toe:modify var="name" toe:pow="number" />`

## Control structures

### `if` control structure

`<tag toe:if="expression">`

### `for` loop

`<tag toe:for="expression">`

In this implemetation of `for` loop syntax for the expression is `item in items`. Where `items` needs to be a list, a set, a tuple or a sequence.

Warning: `item` (or different name defined in the expression) will be created in `for` loop's variable scope. In case you need to access variable in parent scope to for loop's you need to go through `parent.variable_name`.

### `while` loop

`<tag toe:while="expression">`

## Modifying content inside of tags

`<tag toe:value="value" />`

`<tag toe:content="value">`

`<tag toe:computed-value="value" />`

`<tag toe:computed-content="value">`