if exists("b:current_syntax")
  finish
endif
let b:current_syntax = "urtext"

syntax clear

syntax match urtextAnchor /^\s*\./
syntax region urtextNodePointer start=+|+ end=+>>+ contains=urtextLinkOpeningWrapper, urtextPointerClosingWrapper, urtextLinkContent transparent keepend
syntax region urtextFileLink start=+|/+ end=+>+ contains=urtextLinkOpeningWrapper, urtextLinkClosingWrapper, urtextLinkContent transparent keepend
syntax match urtextNodeLink +|[^>]\{-}>+ contains=urtextLinkOpeningWrapper,urtextLinkClosingWrapper,urtextLinkContent
syntax match urtextBraces /[{}]/
syntax region urtextTimestamp start=+<+ end=+>+ 
syntax match urtextTitle /\w\+ _/
syntax match urtextLinkOpeningWrapper /|/ contained containedin=urtextNodeLink keepend
syntax match urtextLinkClosingWrapper />/ contained containedin=urtextNodeLink keepend
syntax match urtextPointerClosingWrapper />>/ contained containedin=urtextNodeLink
"syntax match urtextLinkContent /\[^|>]\+\ze/ contained containedin=urtextNodeLink
syntax match urtextLinkContent /[^|>]\+/ contained containedin=urtextNodeLink
syntax match urtextHash /#\w\+/
syntax region urtextFrame start="\[\[" end="\]\]" contains=urtextFrameOpeningWrapper, urtextAnchor, urtextFrameClosingWrapper, urtextCall transparent keepend
syntax match urtextFrameOpeningWrapper /\[\[/ contained containedin=urtextFrame
syntax match urtextFrameClosingWrapper /\]\]/ contained containedin=urtextFrame
syntax match urtextCall /\<[A-Z]\+\>/ contained containedin=urtextFrame


highlight urtextAnchor ctermfg=DarkGreen
highlight urtextFrameOpeningWrapper ctermfg=DarkGreen guifg=DarkGreen
highlight urtextFrameClosingWrapper ctermfg=DarkGreen guifg=DarkGreen
highlight urtextCall gui=bold cterm=bold
highlight urtextHash gui=bold cterm=bold
highlight urtextBraces ctermfg=Red guifg=Red
highlight urtextTimestamp ctermfg=Green guifg=Green ctermbg=NONE guibg=NONE
highlight urtextTitle gui=bold cterm=bold
highlight urtextLinkOpeningWrapper gui=bold cterm=bold
highlight urtextLinkClosingWrapper gui=bold cterm=bold
highlight urtextLinkContent ctermfg=Blue guifg=Blue

syntax sync fromstart
