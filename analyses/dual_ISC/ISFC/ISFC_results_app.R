
library(shiny)
library(tidyverse)
library(plot.matrix)
library(plotly)
library(RColorBrewer)

# User-defined parameters (immutable)
zthr = 0
nbin = 6

datadir <- paste0(getwd(),"/results_lorenzo")
filetemplate <- paste0(datadir,"/ISFC_Motion-Scrambled_SEED-TARGET_thr200_binNBIN.txt")



# UI
ui <- fluidPage(

  fluidRow(
    column(3,
       radioButtons("R1_left", "ROI 1 left", choices = c("BA44","BA6","PFt"), selected = "BA44")      
    ),
    column(3,
       radioButtons("R2_left", "ROI 2 left", choices = c("BA44","BA6","PFt"), selected = "BA6")      
    ),
    column(3,
           radioButtons("R1_right", "ROI 1 right", choices = c("BA44","BA6","PFt"), selected = "BA6")      
    ),
    column(3,
           radioButtons("R2_right", "ROI 2 right", choices = c("BA44","BA6","PFt"), selected = "PFt")      
    )
  ),
  
  fluidRow(
    column(6,
      plotOutput("CCplot_left")
    ),
    column(6,
      plotOutput("CCplot_right")
    )
  ),
  
  fluidRow(
    column(6,
       plotlyOutput("sankey_left")    
    ),
    column(6,
       plotlyOutput("sankey_right")    
    )
  )
  

)



# Server logic
server <- function(input, output) {

  # left
  observe({
    output$CCplot_left <- renderPlot(
      draw_CC(input$R1_left, input$R2_left)
    ) 
    
    output$sankey_left <- renderPlotly(
      draw_sankey(input$R1_left, input$R2_left, nbin, zthr)
    ) 
  })
  
  
  # right
  observe({
    output$CCplot_right <- renderPlot(
      draw_CC(input$R1_right, input$R2_right)
    ) 
    
    output$sankey_right <- renderPlotly(
      draw_sankey(input$R1_right, input$R2_right, nbin, zthr)
    ) 
  })
    
}


# function to draw the sankey
draw_sankey <- function(R1, R2, nbin, zthr) {
  
  CC_file <- str_replace_all(filetemplate, c("SEED" = R1, "TARGET" = R2, "NBIN" = nbin))
  CC <- read.table(CC_file, header = F, sep = " ") %>% as.matrix()
  
  R1_names <- map(1:nbin, ~ paste0(R1,"_",.x))
  R2_names <- map(1:nbin, ~ paste0(R2,"_",.x))
  
  rownames(CC) <- R1_names
  colnames(CC) <- R2_names
  
  idx <- which(CC > zthr, arr.ind = T)
  source <- idx[,1] - 1
  target <- idx[,2] - 1 + nbin
  vals <- CC[idx]
  
  # Prepare color palettes
  
  # The one below is inspired to the library(wesanderson)
  # palette: wes_palette("Zissou1", 6, type = "continuous") 
  WES <- c("#78B7C5","#78B7C5", "#E1AF00","#E1AF00", "#F21A00","#F21A00")
  
  REDS <- colorRampPalette(c(brewer.pal(5,"Reds")[2],brewer.pal(5,"Reds")[5]))
  GREENS <- colorRampPalette(c(brewer.pal(5,"Greens")[2],brewer.pal(5,"Greens")[5]))
  BLUES <- colorRampPalette(c(brewer.pal(5,"Blues")[2],brewer.pal(5,"Blues")[5]))
  
  # prepare link_colors by generating a named character that will be used as a lookup
  # https://www.infoworld.com/article/3323006/do-more-with-r-quick-lookup-tables-using-named-vectors.html
  # link_colors_lookup <- brewer.pal(dim(CC)[1],"Reds")
  link_colors_lookup <- WES
  names(link_colors_lookup) <- rownames(CC)
  link_colors <- map_chr(names(source), ~ link_colors_lookup[.x] %>% unname() %>% toRGB(alpha = 0.3))
  
  # # Specification of the x,y position does not really work...
  # x_pos <- c(rep(0,nbin),rep(1,nbin))
  # y_pos <- rep(seq(1:nbin),2)
  
  plot_ly(
    type = "sankey",
    domain = list(
      x =  c(0,1),
      y =  c(0,1)
    ),
    arrangement = "snap", hoverinfo = "skip", 
    textfont = list(family = "Arial"),
    orientation = "h",
    node = list(
      label = c(R1_names, R2_names),
      # x = x_pos/max(x_pos),
      # y = y_pos/max(y_pos),
      color = c(WES, WES),
      pad = 5,
      thickness = 20
    ),
    link = list(
      source = source,
      target = target,
      value = CC[idx],
      color = link_colors
    )
  )
  
}






# function to draw the CC
draw_CC <- function(R1, R2) {
  
  CC_file <- str_replace_all(filetemplate, c("SEED" = R1, "TARGET" = R2, "NBIN" = nbin))
  CC <- read.table(CC_file, header = F, sep = " ") %>% as.matrix()
  
  R1_names <- map(1:nbin, ~ paste0(R1,"_",.x))
  R2_names <- map(1:nbin, ~ paste0(R2,"_",.x))
  
  rownames(CC) <- R1_names
  colnames(CC) <- R2_names
  
  # # digits inside and no colorbar
  # CC %>% plot(
  #   asp=T, digits=2, col=brewer.pal(9,"Reds"), key=NULL,
  #   axis.col = list(side=1, las=2),
  #   axis.row = list(side=2, las=1)
  # )
  
  # no digits and colorbar
  CC %>% plot(
    asp=T, col=brewer.pal(9,"Reds"),
    axis.col = list(side=1, las=2),
    axis.row = list(side=2, las=1)
  )
  
}




# Run the application 
shinyApp(ui = ui, server = server)











