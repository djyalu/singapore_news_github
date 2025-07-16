module.exports = async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    return res.status(200).json({ 
        status: 'ok',
        timestamp: new Date().toISOString(),
        message: 'API is running'
    });
};