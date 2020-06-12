library(tidyverse)
library(latex2exp)
library(scales)
library(extrafont)
library(viridis)
library(ggridges)
library(forcats)
# set fonts
loadfonts(device = "pdf")
# font_import()
# link www.fontsquirrel.com/fonts/latin-modern-roman

# execute once to add fonts:
# font_import(pattern = "lmroman*")
# theme(legend.position = "top", text=element_text(size=14, family="LM Roman 10"))

# set ggplot global theme
theme_set(theme_bw() +
            theme(legend.position = "top") +
            theme(text = element_text(size = 16, family = "LM Roman 10")))

# multiple figures together
if(!require(devtools)) install.packages("devtools")
devtools::install_github("thomasp85/patchwork")
library(patchwork)