if exists("b:current_syntax")
  finish
endif
let b:current_syntax = "Urtext"

syntax clear

syntax region UrtextNodePointer start=+|+ end=+>>+ oneline contains=UrtextLinkOpeningWrapper, UrtextPointerClosingWrapper, UrtextLinkContent transparent keepend

syntax region UrtextFileLink start=+|/+ end=+>+ oneline contains=UrtextLinkOpeningWrapper, UrtextLinkClosingWrapper, UrtextLinkContent transparent keepend

syntax match UrtextNodeLink +|[^>]\{-}>+ oneline contains=UrtextLinkOpeningWrapper,UrtextLinkClosingWrapper,UrtextLinkContent

syntax region UrtextFrame start="\[\[" end="\]\]" contains=UrtextFrameOpeningWrapper, UrtextAnchor, UrtextFrameClosingWrapper, UrtextCall transparent keepend

syntax match UrtextBraces /[{}]/
highlight default link UrtextBraces Special

syntax region UrtextTimestamp start=+<+ end=+>+ 
highlight default link UrtextTimestamp String

syntax match UrtextTitle "{\=\zs[[:alnum:][:punct:] ]\+ _" 
highlight default link UrtextTitle Title

syntax match UrtextLinkOpeningWrapper /|/ contained containedin=UrtextNodeLink keepend
highlight default link UrtextLinkOpeningWrapper Special

syntax match UrtextLinkClosingWrapper />/ contained containedin=UrtextNodeLink keepend
highlight default link UrtextLinkClosingWrapper Special

syntax match UrtextPointerClosingWrapper />>/ contained containedin=UrtextNodeLink
highlight default link UrtextPointerClosingWrapper Special

syntax match UrtextLinkContent /[^|>]\+/ contained containedin=UrtextNodeLink
highlight default link UrtextLinkContent Title

syntax match UrtextHash /#\w\+/
highlight default link UrtextHash UrtextHashStyle

syntax match UrtextFrameOpeningWrapper /\[\[/ contained containedin=UrtextFrame
highlight default link UrtextFrameOpeningWrapper Special

syntax match UrtextFrameClosingWrapper /\]\]/ contained containedin=UrtextFrame
highlight default link UrtextFrameClosingWrapper Special

syntax match UrtextCall /\<[A-Z]\+\>/ contained containedin=UrtextFrame
highlight default link UrtextCall Function

syntax match UrtextMetaKey /\k\+\ze::/ nextgroup=UrtextMetaAssigner
highlight default link UrtextMetaKey Constant

syntax match UrtextMetaAssigner /::/ oneline contained nextgroup=UrtextMetaValues
highlight default link UrtextMetaAssigner Special

syntax match UrtextMetaValues /[^;\n]\+/ oneline contained
highlight default link UrtextMetaValues String

syntax match UrtextSuffix /\.[A-Za-z0-9_-]\+/ contained
highlight default link UrtextSuffix Type

"syntax match UrtextTimestamp /<\d\{4}-\d\{2}-\d\{2}>/ contained
"highlight default link UrtextTimestamp Number

syntax sync fromstart