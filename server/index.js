const express = require("express")
const bodyParser = require('body-parser');
const app = express()
const axios = require('axios');

const PORT = 3000;

app.use(express.urlencoded({extended: true}))
app.use(bodyParser.json());

app.get('/searchBySimilarities', (req, res) => {
    res.render("searchBySimilarities.ejs");
})

app.get('/searchByTags', (req, res) => {
    res.render("searchByTags.ejs");
})


app.get('/', (req, res) => {
    res.render("index.ejs");
})

const pythonServerURL = 'http://pythonServer:5000';

app.post('/searchByTagsInPython', async (req, res) => {

    var searchingBy = req.body.searchType;
    var tags = req.body.tags;
    console.log(tags, searchingBy);

        const recommendationResponse = await axios.post(`${pythonServerURL}/searchByTagsInPython`, {
          searchingBy:searchingBy, tags:tags
        })

            const resultData = recommendationResponse.data.result;

            let titles = resultData['title'];
            let synopsis = resultData['synopsis'];
            let scores = resultData['score'];
            let icons = resultData['icon'];
           
          var responseData = {
             array: titles,
             scores: scores,
             descriptions: synopsis,
             icons: icons
           };
        
           res.json(responseData);
          
});

app.post('/searchBySimilaritiesInPython', async (req, res) => {

    var amount = req.body.amount;
    var animeName = req.body.animeName;

    const recommendationResponse = await axios.post(`${pythonServerURL}/searchBySimilaritiesInPython`, {
        animeName:animeName, amount:amount
      })
      
          const resultData = recommendationResponse.data.result;

          let titles = resultData['title'];
          let synopsis = resultData['synopsis'];
          let scores = resultData['score'];
          let icons = resultData['icon'];
         
        var responseData = {
           array: titles,
           scores: scores,
           descriptions: synopsis,
           icons: icons
         };
      
         res.json(responseData);
        
});



app.listen(PORT, () => {
    console.log("Listening");
})
