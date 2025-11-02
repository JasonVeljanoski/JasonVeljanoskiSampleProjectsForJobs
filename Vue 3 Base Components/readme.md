# Documentation Base Components

## BaseBtn

A versatile button component that supports various styles, sizes, and states.

### Props

| Prop Name   | Type | Default Value | Description                                                                                                          |
|-------------|------|---------------|----------------------------------------------------------------------------------------------------------------------|
| active      | boolean | `undefined` | Sets the button in active state                                                                                      |
| icon        | string | `undefined` | Icon name to display (loaded from `@icons/[name].svg`)                                                               |
| disabled    | boolean | `false` | Disables the button when true                                                                                        |
| loading     | boolean | `false` | Shows loading animation when true                                                                                    |
| activeStyle | Record<string, string> \| string | `undefined` | Custom styles to be applied when button is active. Can be an object of style properties or a string of inline styles |
| iconStyle   | Record<string, string> \| string | `undefined` | Custom styles to be applied on icon (if exists). Can be an object of style properties or a string of inline styles   |
| size        | 'small' \| 'default' \| 'large' | `'default'` | Button size variant                                                                                                  |
| color       | string | `undefined` | Custom color (CSS color or CSS variable starting with '--')                                                          |
| outlined    | boolean | `false` | Creates outlined variant                                                                                             |
| text        | boolean | `false` | Creates text variant                                                                                                 |
| iconPosition | string  | 'left' | Sets the position of the icon. Possible values: 'left' or 'right'. |

### Slots

- Default slot: Button content (text)
- Icon: Automatically rendered if `icon` prop is provided

## BaseDialog

A modal dialog component that provides a flexible container for content with overlay support.

### Props

| Prop Name | Type | Default Value | Description |
|-----------|------|---------------|-------------|
| modelValue | boolean | `false` | Controls the visibility of the dialog |
| closeOnContentClick | boolean | `false` | Closes the dialog when clicking on content area |
| disabled | boolean | `false` | Disables the dialog when true |
| maxWidth | string \| number | `null` | Maximum width of the dialog content |
| persistent | boolean | `false` | Prevents closing on outside click or ESC key |
| scrim | string \| boolean | `true` | Background overlay color or visibility |

### Slots

- activator: Trigger element with click handler
- default: Main content area

### Events

- update:modelValue: Emitted when dialog visibility changes

## BaseCard

A container component that provides structured content areas with optional header and footer.

### Props

| Prop Name | Type | Default Value | Description |
|-----------|------|---------------|-------------|
| title | string | `''` | Card title text (used when header slot is not provided) |

### Slots

- header: Custom header content (replaces title prop)
- default: Main content area
- footer: Optional footer area with actions


## BaseBtnToggle

A button group component that allows selection between multiple options, similar to a radio group but with button styling.

### Props

| Prop Name | Type | Default Value | Description |
|-----------|------|---------------|-------------|
| modelValue | number \| number[] | `0` | The index or array of indices of selected button(s). Uses array when `multiple` is true |
| divided | boolean | `false` | Adds spacing between buttons and a background container |
| disabled | boolean | `false` | Disables all buttons in the group |
| mandatory | boolean \| 'force' | `false` | Controls selection behavior. If `true`, prevents deselection of current item(s). If `'force'`, always requires at least one selection |
| vertical | boolean | `false` | Arranges buttons in a vertical stack instead of horizontal row |
| multiple | boolean | `false` | Enables multiple button selection mode. When true, modelValue becomes an array of indices |

### Events

| Event Name        | Payload Type | Description |
|-------------------|--------------|-------------|
| update:modelValue | number | Emitted when selection changes. Returns button index or -1 if deselected |

## BaseTextField

| Prop Name | Type | Default Value | Description                                                                                                                                                                                                                                                                                                    |
|-----------|------|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| modelValue | any | `undefined` | The value bound to the input field using v-model                                                                                                                                                                                                                                                               |
| type | string | `'text'` | Sets input type (e.g. 'text', 'password', 'email', 'number')                                                                                                                                                                                                                                                   |
| label | string | `undefined` | Label text displayed above the input field                                                                                                                                                                                                                                                                     |
| labelPosition | 'float' \| 'inside' | `'float'` | Position of the label - either floating above or inside the input |
| placeholder | string | `undefined` | Placeholder text shown when input is empty                                                                                                                                                                                                                                                                     |
| loading | boolean | `false` | Shows a loading progress bar animation below the input                                                                                                                                                                                                                                                         |
| clearable | boolean | `false` | Shows a clear button when input has value                                                                                                                                                                                                                                                                      |
| disabled | boolean | `null` | Disables the input field when true                                                                                                                                                                                                                                                                             |
| maxWidth | string/number | `undefined` | Sets maximum width in pixels                                                                                                                                                                                                                                                                                   |
| minWidth | string/number | `undefined` | Sets minimum width in pixels                                                                                                                                                                                                                                                                                   |
| width | string/number | `undefined` | Sets fixed width in pixels                                                                                                                                                                                                                                                                                     |
| error | boolean | `false` | Manually sets error state                                                                                                                                                                                                                                                                                      |
| errorMessages | string/string[] | `[]` | Custom error message(s) to display                                                                                                                                                                                                                                                                             |
| rules | ValidationRule[] | `[]` | Accepts types: `function`, `boolean` and `string`. Functions pass an input value as an argument and must return either `boolean` or `string` containing an error message. The input field will enter an error state if a function returns `false` or `string`, or returned array contains `false` or `string`. |

### Events

| Event Name | Payload Type | Description                           |
|------------|--------------|---------------------------------------|
| update:modelValue | any          | Emitted when input value changes      |
| error | boolean      | Emitted when validation state changes |
| click:clear       | null         | Emitted when input cleared            |

### Slots

`#appendInner`: Slot for appendInnerIcon location

### ValidationRule Type

A validation rule can be:
```js
type ValidationResult = string | boolean | PromiseLike<string | boolean>;
type ValidationRule = ValidationResult | ((value: any) => ValidationResult);
```

Rules can return:
- `true`: validation passed
- `string`: validation failed (error message)
- `Promise<boolean | string>`: for async validation

Other notes:
- Rules are evaluated in order
- Only the first failing rule's message will be displayed
- Empty rules array `[]` means no validation

### Attr Inherited
The HTML input element in this component is set to receive any additional attributes, events, or listeners passed to parent BaseTextField, such as:
- Native HTML input attributes (e.g., `autocomplete`, `name`, `required`)
- Event listeners (e.g., `@focus`, , `@keydown`) `@blur`

# BaseCheckbox

A customizable checkbox component that supports various states and styling options.

### Props

| Prop Name | Type | Default Value | Description |
|-----------|------|---------------|-------------|
| modelValue | boolean | `required` | Controls the checked state of the checkbox |
| color | string | `undefined` | Custom color (CSS color or CSS variable starting with '--') |
| disabled | boolean | `null` | Removes the ability to click or target the component |
| label | string | `undefined` | Text label for the checkbox |

### Events

| Event Name | Payload Type | Description |
|------------|--------------|-------------|
| update:modelValue | boolean | Emitted when checkbox state changes |

### Slots

- Default slot: Custom label content (used when label prop is not provided)
