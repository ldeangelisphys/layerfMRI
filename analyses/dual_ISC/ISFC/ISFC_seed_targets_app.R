
library(shiny)
library(tidyverse)
library(plot.matrix)
library(plotly)
library(RColorBrewer)

# Define UI for application that draws a histogram
ui <- fluidPage(

  fluidRow(
    column(2,
       radioButtons("S", "seed", choices = c("BA44","BA6","PFt"), selected = "BA44")      
    ),
    column(2,
       radioButtons("T1", "1st target", choices = c("BA44","BA6","PFt"), selected = "BA6")      
    ),
    column(2,
       radioButtons("T2", "2nd target", choices = c("BA44","BA6","PFt"), selected = "PFt")      
    )
  ),
  
  fluidRow(
    column(3,
      plotOutput("seed_to_T1")
    ),
    column(3,
      plotOutput("T1_to_T2")
    )
  ),
  
  fluidRow(
    column(6,
       plotlyOutput("sankey")    
    )
  )
  

)

nbin=6

datadir <- paste0(getwd(),"/results_lorenzo")
filetemplate <- paste0(datadir,"/ISFC_Motion-Scrambled_SEED-TARGET_thr200_binNBIN.txt")

# Define server logic required to draw a histogram
server <- function(input, output) {

  observe({
  
    seed_auto_file <- str_replace_all(filetemplate, c("SEED"=input$S, "TARGET"=input$S, "NBIN"=nbin))
    seed_t1_file   <- str_replace_all(filetemplate, c("SEED"=input$S, "TARGET"=input$T1, "NBIN"=nbin))
    t1_t2_file     <- str_replace_all(filetemplate, c("SEED"=input$T1, "TARGET"=input$T2, "NBIN"=nbin))
    
    seed_auto <- read.table(seed_auto_file, header = F, sep = " ") %>% as.matrix()
    seed_t1 <- read.table(seed_t1_file, header = F, sep = " ") %>% as.matrix()
    t1_t2 <- read.table(t1_t2_file, header = F, sep = " ") %>% as.matrix()
    
    seed_names <- map(1:nbin, ~ paste0(input$S,"_",.x))
    t1_names <- map(1:nbin, ~ paste0(input$T1,"_",.x))
    t2_names <- map(1:nbin, ~ paste0(input$T2,"_",.x))
    
    # seed-to-seed names
    rownames(seed_auto) <- seed_names
    colnames(seed_auto) <- seed_names

    # seed_to_t1 names
    rownames(seed_t1) <- seed_names
    colnames(seed_t1) <- t1_names
    
    # t1 to t2 names
    rownames(t1_t2) <- t1_names
    colnames(t1_t2) <- t2_names
    
    output$seed_to_T1 <- renderPlot(
      seed_t1 %>% plot(asp=T, digits=2, col=brewer.pal(9,"Reds"), key=NULL)
    )

    output$T1_to_T2 <- renderPlot(
      t1_t2 %>% plot(asp=T, digits=2, cex=0.5, col=brewer.pal(9,"Reds"), key=NULL)
    )
    
    
    CC <- cbind(seed_auto, seed_t1, t1_t2)
    
    # zero the seed-to-seed correlation
    CC[1:nbin,1:nbin] <- 0

    
    ## plot the sankey
    zthr = 0
    idx <- which(CC > zthr, arr.ind = T)
    
    source <- idx[,1] - 1
    target <- idx[,2] - 1
    
    nbin <- nrow(CC)
    
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
    
    x_pos <- c(rep(0,nbin),rep(1,nbin),rep(2,nbin))
    y_pos <- rep(seq(1:nbin),3)
    
    p <- plot_ly(
      type = "sankey",
      arrangement = "freedom", hoverinfo = "skip", 
      textfont = list(family = "Arial"),
      orientation = "h",
      node = list(
        label = colnames(CC),
        x = x_pos/max(x_pos),
        y = y_pos/max(y_pos),
        color = c(WES, WES, WES),
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
    
    output$sankey <- renderPlotly(p)
    
    
  })

}

# Run the application 
shinyApp(ui = ui, server = server)











