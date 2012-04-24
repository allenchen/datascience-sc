%% 
%% This is file 'handout.cls'

\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{handout}
	      [1999/06/15 v1.0v
 Class handout document class]

\LoadClassWithOptions{article}[1997/06/16]

\RequirePackage{moretext}
\RequirePackage{epsfig}
\RequirePackage{small-captions}
\RequirePackage{multicol}
\RequirePackage[
pdftex,
colorlinks,bookmarks,pagebackref,pdfpagemode=UseOutlines]{hyperref}
\ifx\usetimes\@undefined\else\RequirePackage{times}\fi

%    ****************************************
%    *         EXERCISES 	            *
%    ****************************************
%

\newcounter{exerciseCounter}

\newenvironment{exercise}{\refstepcounter{exerciseCounter}\paragraph{\theexerciseCounter.}}{}

%    ****************************************
%    *         TITLE AND ABSTRACT           *
%    ****************************************
%

\renewcommand{\maketitle}{\par
 \@spoil\begingroup
 \def\thefootnote{\fnsymbol{footnote}}
 \def\@makefnmark{\hbox 
 to 0pt{$^{\@thefnmark}$\hss}}
 \if@twocolumn 
 \twocolumn[\@maketitle] 
 \else \newpage
 \global\@topnum\z@ \@maketitle \fi\thispagestyle{plain}\@thanks
 \endgroup
 \setcounter{footnote}{0}
 \let\maketitle\relax
 \let\@maketitle\relax
 \gdef\@thanks{}\gdef\thanks##1{}
 \markboth{\instructor@}{\@spoil\runningtitle@}
 \gdef\@author{}\gdef\@title{}}
\def\@maketitle{\newpage
    \begin{center}
	UNIVERSITY OF CALIFORNIA \\
	Department of Electrical Engineering \\
	and Computer Sciences \\
	Computer Science Division
    \end{center}
    \vspace{1em}
    {\bf
      \begin{multicols}{2}
        \noindent\courseNumber@\\
        \semester@\\
        
        \columnbreak
        \begin{raggedleft}\instructor@\end{raggedleft}
      \end{multicols}
	\vspace{0.5em}
	\begin{center}
	   \@title\@credits
	\end{center}
    }
    \ifx\@empty\due@ \else\vspace{0.5em}\begin{tabbing} \due@ \end{tabbing}\fi
    \begingroup\let\\=\relax
    \endgroup
}

\newcommand{\makecompacttitle}{\par
 \@spoil\begingroup
 \def\thefootnote{\fnsymbol{footnote}}
 \def\@makefnmark{\hbox 
 to 0pt{$^{\@thefnmark}$\hss}}
 \if@twocolumn 
 \twocolumn[\@makecompacttitle] 
 \else \newpage
 \global\@topnum\z@ \@makecompacttitle \fi
 \thispagestyle{plain}\@thanks
 \endgroup
 \setcounter{footnote}{0}
 \let\makecompacttitle\relax
 \let\@makecompacttitle\relax
 \markboth{\instructor@}{\@spoil\runningtitle@}
 \gdef\@thanks{}\gdef\thanks##1{}
 \gdef\@author{}\gdef\@title{}}
\def\@makecompacttitle{\newpage
    \noindent\hbox to \textwidth{\bf
	    \courseNumber@, \semester@ \hfill \@title\@credits \hfill \instructor@}
    \par\vspace{\baselineskip}
    \ifx\@empty\due@ \else\noindent\due@\par\vspace{\baselineskip}\fi
    \begingroup\let\\=\relax
    \endgroup
}

\def\@title{}
\def\@credits{}
\def\courseNumber@{}
\def\due@{}
\def\instructor@{}
\def\semester@{}
\def\runningtitle@{\@title}

\newcommand{\filetitle}[1]{\pdfstringdef\@pdftitle{#1}%
			   \renewcommand{\title}[1]{\def\@title{##1}}}
\renewcommand{\title}[1]{\def\@title{#1}\pdfstringdef\@pdftitle{#1}}
\newcommand{\credits}[1]{\def\@credits{\thanks{~#1}}}
\newcommand{\course}[1]{\def\courseNumber@{#1}}
\newcommand{\due}[1]{\def\due@{{\bf Due:} #1}}
\newcommand{\instructor}[1]{\def\instructor@{#1}\pdfstringdef\@pdfauthor{#1}}
\renewcommand{\author}[1]{\instructor{#1}}
\newcommand{\semester}[1]{\def\semester@{#1}}
\newcommand{\runningtitle}[1]{\def\runningtitle@{#1}}

\def\@spoil{\ifx\discourageprinting\@undefined\else\special{" [ /DataSource (quit) /PS pdfmark}\fi}

\def\m@#1{\ifmmode#1\else$#1$\fi}
\def\dogt@{\m@>}
\def\dolt@{\m@<}
{\catcode`\<=\active\catcode`\>=\active
 \gdef\nicegtlt{
	\catcode`\<=\active\catcode`\>=\active\def>{\dogt@}\def<{\dolt@}}}

\pagestyle{myheadings}

\endinput
