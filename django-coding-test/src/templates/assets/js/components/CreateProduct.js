import React, {useState, useEffect} from 'react';
import TagsInput from 'react-tagsinput';
import 'react-tagsinput/react-tagsinput.css';
import Dropzone from 'react-dropzone';
import axios from 'axios';
import Cookies from 'js-cookie'; 


const CreateProduct = (props) => {

    const [productVariantPrices, setProductVariantPrices] = useState([]);
    const [productName, setProductName] = useState('');
    const [productSKU, setProductSKU] = useState('');
    const [productDescription, setProductDescription] = useState('');
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [csrfToken, setCSRFToken] = useState('');

    // Effect hook to fetch CSRF token from cookies on component mount
    useEffect(() => {
        const csrfTokenFromCookies = Cookies.get('csrftoken');
        setCSRFToken(csrfTokenFromCookies);
    }, []);

    

    const [productVariants, setProductVariant] = useState([
        {
            option: 1,
            tags: []
        }
    ])
    console.log(typeof props.variants)
    // handle click event of the Add button
    const handleAddClick = () => {
        let all_variants = JSON.parse(props.variants.replaceAll("'", '"')).map(el => el.id)
        let selected_variants = productVariants.map(el => el.option);
        let available_variants = all_variants.filter(entry1 => !selected_variants.some(entry2 => entry1 == entry2))
        setProductVariant([...productVariants, {
            option: available_variants[0],
            tags: []
        }])
    };

    // handle input change on tag input
    const handleInputTagOnChange = (value, index) => {
        let product_variants = [...productVariants]
        product_variants[index].tags = value
        setProductVariant(product_variants)

        checkVariant()
    }

    // remove product variant
    const removeProductVariant = (index) => {
        let product_variants = [...productVariants]
        product_variants.splice(index, 1)
        setProductVariant(product_variants)
    }

    // check the variant and render all the combination
    const checkVariant = () => {
        let tags = [];

        productVariants.filter((item) => {
            tags.push(item.tags)
        })

        setProductVariantPrices([])

        getCombn(tags).forEach(item => {

            setProductVariantPrices(productVariantPrice => [...productVariantPrice, {
                title: item,
                price: 0,
                stock: 0
            }])
        })

    }

    // combination algorithm
    function getCombn(arr, pre) {
        pre = pre || '';
        if (!arr.length) {
            return pre;
        }
        let ans = arr[0].reduce(function (ans, value) {
            return ans.concat(getCombn(arr.slice(1), pre + value + '/'));
        }, []);
        return ans;
    }
    
    // update product variant price
    const handlePriceChange = (index, value) => {
        setProductVariantPrices((prevPrices) => {
          const updatedPrices = [...prevPrices];
          updatedPrices[index].price = value;
          return updatedPrices;
        });
      };
      
    // update product variant stock value  
      const handleStockChange = (index, value) => {
        setProductVariantPrices((prevPrices) => {
          const updatedPrices = [...prevPrices];
          updatedPrices[index].stock = value;
          return updatedPrices;
        });
      };
      
    
  // Save product
  const saveProduct = async (event) => {
    event.preventDefault();

    // Check if required fields are filled up
    if (!productName || !productSKU || !productDescription) {
      alert('Please fill up all required fields (Product Name, Product SKU, Description)');
      return;
    }

    try {
      // Create a Product model object
      const productData = {
        title: productName,
        sku: productSKU,
        description: productDescription
      };

    //   const csrfToken = 'DVp61MiBb2hlI1VhdNDaEtLJPXMW4iO4Qw8zFfDUZGSct2DESs55KW0Zweryi2NB';   // temporary solution
      const headers = {
            'X-CSRFToken': csrfToken,
       };
       console.log("csrf_token");
       console.log(csrfToken);

      const response = await axios.post('/product/api/create/', productData, { headers });

      // Create ProductVariant and ProductVariantPrice model objects
      const productId = response.data.id;

      const variantItems = productVariants.map((variant, index) => {

        // Check if variant tags exist and split them if there are multiple tags
        if (variant.tags.length > 0) {
            variant.tags.forEach((tag) => {
        
            const variantData = {
                variant_title: tag,
                variant: variant.option,
                product: productId,
            };

            axios.post('/product/api/create/product-variants/', variantData, { headers });

            });
        }

      // Create ProductVariantPrice model object
      const variantPriceData = {
        title: productVariantPrices[index].title,
        price: productVariantPrices[index].price,
        stock: productVariantPrices[index].stock,
        product: productId,
      };
      console.log("Product Variation Price");
      console.log(variantPriceData);
      axios.post('/product/api/create/product-variant-prices/', variantPriceData, { headers });

      });

      setTimeout(() => {
      }, 5000); // 10000 milliseconds = 10 seconds
      console.log("5 sec after");
      // Upload product images
    const formData = new FormData();
    uploadedFiles.forEach((file) => {
      formData.append('file', file);
    });


    const uploadResponse = await axios.post(`/product/api/create/${productId}/upload_images/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': csrfToken,
      },
    });
	
	 if (uploadResponse.status === 200) {
      alert('Product and Images saved successfully!');
      // You can redirect to a new page or perform any other action after saving the product.
    } else {
      alert('Error while uploading images. Please try again.');
    }



      // You can redirect to a new page or perform any other action after saving the product.
    } catch (error) {
      alert('Error while saving the product. Please try again.');
      console.error(error);
    }
  };
    


    return (
        <div>
            <section>
                <div className="row">
                    <div className="col-md-6">
                        <div className="card shadow mb-4">
                            <div className="card-body">
                                <div className="form-group">
                                    <label htmlFor="">Product Name</label>
                                    <input type="text" placeholder="Product Name" 
                                           className="form-control" value={productName}
                                           onChange={(e) => setProductName(e.target.value)}/>
                                </div>
                                <div className="form-group">
                                    <label htmlFor="">Product SKU</label>
                                    <input type="text" placeholder="Product Name"
                                           className="form-control" value={productSKU}
                                           onChange={(e) => setProductSKU(e.target.value)}/>
                                </div>
                                <div className="form-group">
                                    <label htmlFor="">Description</label>
                                    <textarea id="" cols="30" rows="4" 
                                              className="form-control" value={productDescription}
                                              onChange={(e) => setProductDescription(e.target.value)}></textarea>
                                </div>
                            </div>
                        </div>

                        <div className="card shadow mb-4">
                            <div
                                className="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 className="m-0 font-weight-bold text-primary">Media</h6>
                            </div>
                            <div className="card-body border">
                                <Dropzone onDrop={acceptedFiles => setUploadedFiles(acceptedFiles)}>
                                    {({getRootProps, getInputProps}) => (
                                        <section>
                                            <div {...getRootProps()}>
                                                <input {...getInputProps()} />
                                                {/* <p>Drag 'n' drop some files here, or click to select files</p> */}
                                                {uploadedFiles.length > 0 ? (
                                                <ul>
                                                    {uploadedFiles.map(file => (
                                                    <li key={file.name}>{file.name}</li>
                                                    ))}
                                                </ul>
                                                ) : (
                                                <p>Drag 'n' drop some files here, or click to select files</p>
                                                )}
                                            </div>
                                        </section>
                                    )}
                                </Dropzone>
                            </div>
                        </div>
                    </div>

                    <div className="col-md-6">
                        <div className="card shadow mb-4">
                            <div
                                className="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 className="m-0 font-weight-bold text-primary">Variants</h6>
                            </div>
                            <div className="card-body">

                                {
                                    productVariants.map((element, index) => {
                                        return (
                                            <div className="row" key={index}>
                                                <div className="col-md-4">
                                                    <div className="form-group">
                                                        <label htmlFor="">Option</label>
                                                        <select className="form-control" defaultValue={element.option}>
                                                            {
                                                                JSON.parse(props.variants.replaceAll("'", '"')).map((variant, index) => {
                                                                    return (<option key={index}
                                                                                    value={variant.id}>{variant.title}</option>)
                                                                })
                                                            }

                                                        </select>
                                                    </div>
                                                </div>

                                                <div className="col-md-8">
                                                    <div className="form-group">
                                                        {
                                                            productVariants.length > 1
                                                                ? <label htmlFor="" className="float-right text-primary"
                                                                         style={{marginTop: "-30px"}}
                                                                         onClick={() => removeProductVariant(index)}>remove</label>
                                                                : ''
                                                        }

                                                        <section style={{marginTop: "30px"}}>
                                                            <TagsInput value={element.tags}
                                                                       style="margin-top:30px"
                                                                       onChange={(value) => handleInputTagOnChange(value, index)}/>
                                                        </section>

                                                    </div>
                                                </div>
                                            </div>
                                        )
                                    })
                                }


                            </div>
                            <div className="card-footer">
                                {productVariants.length !== 3
                                    ? <button className="btn btn-primary" onClick={handleAddClick}>Add another
                                        option</button>
                                    : ''
                                }

                            </div>

                            <div className="card-header text-uppercase">Preview</div>
                            <div className="card-body">
                                <div className="table-responsive">
                                    <table className="table">
                                        <thead>
                                        <tr>
                                            <td>Variant</td>
                                            <td>Price</td>
                                            <td>Stock</td>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {
                                            productVariantPrices.map((productVariantPrice, index) => {
                                                return (
                                                    <tr key={index}>
                                                        <td>{productVariantPrice.title}</td>
                                                        <td><input className="form-control" type="text" value={productVariantPrice.price} onChange={(e) => handlePriceChange(index, e.target.value)}/></td>
                                                        <td><input className="form-control" type="text" value={productVariantPrice.stock} onChange={(e) => handleStockChange(index, e.target.value)}/></td>
                                                    </tr>
                                                )
                                            })
                                        }
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <button type="submit" onClick={saveProduct} className="btn btn-lg btn-primary">Save</button>
                <button type="button" className="btn btn-secondary btn-lg">Cancel</button>
            </section>
        </div>
    );
};

export default CreateProduct;
