export const dynamic = 'force-static';

export default function GET(){
    const content = ` # OWASP Nest - Gateway to OWASP                                            
                                                                           
    ## Overview                                                                
    Welcome to OWASP Nest, your gateway to OWASP. Discover, engage, and help sh
                                                                            
    Website: https://nest.owasp.org/                                           
                                                                            
    ## Main Navigation                                                         
                                                                            
    ### OWASP Nest                                                             
    - **About**: https://nest.owasp.org/about - Learn about OWASP Nest         
    - **Contribute**: https://nest.owasp.org/contribute - Get involved and cont
    - **Projects**: https://nest.owasp.org/projects - Browse OWASP projects    
    - **Sponsors**: https://owasp.org/donate/?reponame=www-project-nest&title=O
    - **Contact**: https://owasp.org/contact/ - Get in touch                   
    - **Events**: https://owasp.glueup.com/organization/6727/events/ - Attend O
    - **Teams**: https://owasp.org/corporate/ - Corporate partnerships and team
                                                                            
    ### OWASP Community                                                        
    - **Chapters**: https://nest.owasp.org/chapters - OWASP Local Chapters     
    - **Members**: https://nest.owasp.org/members - Community members          
    - **Organizations**: https://nest.owasp.org/organizations - Partner organiz
    - **Snapshots**: https://nest.owasp.org/snapshots - Community snapshots    
    - **Community Hub**: https://owasp.org/www-community/ - Main community reso
                                                                            
    ### OWASP Resources                                                        
    - **Chapters**: https://nest.owasp.org/chapters - Local chapter directory  
    - **Contribute**: https://nest.owasp.org/contribute - Contribution opportun
    - **Committees**: https://nest.owasp.org/committees - OWASP committees     
    - **Projects**: https://nest.owasp.org/projects - Official OWASP projects  
                                                                            
    ## About OWASP                                                             
    The Open Worldwide Application Security Project (OWASP) is a nonprofit foun
                                                                            
    ## How to Get Started                                                      
    1. **Explore Projects**: Visit the projects page to discover active OWASP s
    2. **Join the Community**: Connect with local chapters and members         
    3. **Contribute**: Find ways to contribute your skills and expertise       
    4. **Stay Informed**: Subscribe to events and community updates            
    5. **Get Support**: Reach out through the contact page for questions 
`
    return new Response(content, {
        headers:{
            'Content-Type': 'text/plain'
        }
    })
}