# WebVTT Conversion Utility

## Quickstart

```console
python -m http.server
```

## Test Input Examples

1. Paste text from one of the examples into the input `<textarea>`
2. Click "Convert to WebVTT"
3. Tab should automatically switch to "Output" and fully valid WebVTT should be displayed in the output `<textarea>`.

## Test Validator

1. Paste the text from `./examples/invalid.vtt` directly into the output `<textarea>`. It should automatically validate and erros listed on the side.
2. Click on a validation error to select the and scroll to that line.
3. Fix the error according to the message. That error should be removed from the list.